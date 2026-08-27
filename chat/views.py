from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.views.decorators.http import require_POST

from matching.models import Match, DateProposal
from accounts.models import Profile, BlockRecord
from .models import Message, MessageReaction
from .ai_service import generate_spark_icebreakers


@login_required
def inbox_view(request):
    """
    Optimized inbox view displaying active match conversations with unread counts.
    """
    # Exclude blocked users
    blocked_by_me = BlockRecord.objects.filter(blocker=request.user).values_list('blocked_user_id', flat=True)
    blocking_me = BlockRecord.objects.filter(blocked_user=request.user).values_list('blocker_id', flat=True)
    blocked_ids = set(blocked_by_me).union(set(blocking_me))

    matches_qs = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user),
        is_active=True
    ).exclude(
        Q(user1_id__in=blocked_ids) | Q(user2_id__in=blocked_ids)
    ).select_related(
        'user1__profile', 'user2__profile'
    ).prefetch_related(
        Prefetch('messages', queryset=Message.objects.order_by('-timestamp'))
    )
    
    conversations = []
    for match in matches_qs:
        other_user = match.get_other_user(request.user)
        messages_list = list(match.messages.all())
        last_message = messages_list[0] if messages_list else None
        unread_count = sum(1 for m in messages_list if m.sender_id == other_user.id and not m.is_read)
        
        conversations.append({
            'match': match,
            'other_user': other_user,
            'other_profile': getattr(other_user, 'profile', None),
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    # Sort by latest message timestamp or match creation date
    conversations.sort(
        key=lambda c: c['last_message'].timestamp if c['last_message'] else c['match'].created_at,
        reverse=True
    )
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'chat/inbox.html', context)


@login_required
def conversation_view(request, match_id):
    """
    Real-time conversation view with live WebSocket bridge, AI icebreakers, date planner, and safety tools.
    """
    match = get_object_or_404(
        Match.objects.filter(Q(user1=request.user) | Q(user2=request.user), is_active=True),
        pk=match_id
    )
    other_user = match.get_other_user(request.user)

    # Check if blocked
    if BlockRecord.objects.filter(Q(blocker=request.user, blocked_user=other_user) | Q(blocker=other_user, blocked_user=request.user)).exists():
        messages.error(request, "This conversation is unavailable.")
        return redirect('inbox')
    
    # Handle POST message sending fallback (for non-JS / form submit)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                match=match,
                sender=request.user,
                content=content
            )
            return redirect('conversation', match_id=match.id)
    
    # Mark unread messages from other user as read
    match.messages.filter(sender=other_user, is_read=False).update(is_read=True)
    
    message_list = match.messages.select_related('sender').prefetch_related('reactions').all()
    date_proposals = match.date_proposals.select_related('proposed_by').all()
    
    # Generate initial AI Spark icebreakers
    spark_icebreakers = generate_spark_icebreakers(match, request.user)
    
    context = {
        'match': match,
        'other_user': other_user,
        'other_profile': getattr(other_user, 'profile', None),
        'message_list': message_list,
        'date_proposals': date_proposals,
        'spark_icebreakers': spark_icebreakers,
    }
    return render(request, 'chat/conversation.html', context)


@login_required
def icebreakers_api_view(request, match_id):
    """
    JSON endpoint for dynamic on-demand AI icebreaker generation.
    """
    match = get_object_or_404(
        Match.objects.filter(Q(user1=request.user) | Q(user2=request.user), is_active=True),
        pk=match_id
    )
    icebreakers = generate_spark_icebreakers(match, request.user)
    return JsonResponse({'status': 'success', 'icebreakers': icebreakers})


@login_required
@require_POST
def message_reaction_api_view(request, message_id):
    """
    JSON endpoint for toggling emoji reactions on messages.
    """
    message = get_object_or_404(Message, pk=message_id)
    if message.match.user1 != request.user and message.match.user2 != request.user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    emoji = request.POST.get('emoji', '❤️')
    existing = MessageReaction.objects.filter(message=message, user=request.user, emoji=emoji).first()
    if existing:
        existing.delete()
        added = False
    else:
        MessageReaction.objects.create(message=message, user=request.user, emoji=emoji)
        added = True

    return JsonResponse({'status': 'success', 'added': added, 'emoji': emoji})
