from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max
from matching.models import Match
from .models import Message

@login_required
def inbox_view(request):
    matches_qs = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1__profile', 'user2__profile')
    
    conversations = []
    for match in matches_qs:
        other_user = match.get_other_user(request.user)
        last_message = match.messages.last()
        unread_count = match.messages.filter(sender=other_user, is_read=False).count()
        
        conversations.append({
            'match': match,
            'other_user': other_user,
            'other_profile': getattr(other_user, 'profile', None),
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    # Sort by latest message timestamp or match id
    conversations.sort(
        key=lambda c: c['last_message'].timestamp if c['last_message'] else match.created_at,
        reverse=True
    )
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'chat/inbox.html', context)

@login_required
def conversation_view(request, match_id):
    match = get_object_or_404(
        Match.objects.filter(Q(user1=request.user) | Q(user2=request.user)),
        pk=match_id
    )
    other_user = match.get_other_user(request.user)
    
    # Handle POST message sending
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
    
    message_list = match.messages.select_related('sender').all()
    
    context = {
        'match': match,
        'other_user': other_user,
        'other_profile': getattr(other_user, 'profile', None),
        'message_list': message_list,
    }
    return render(request, 'chat/conversation.html', context)
