/* ============================================================
   LoveMatch — Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

    /* ---- 1. Bootstrap Tooltips ---- */
    var tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });


    /* ---- 2. Auto-dismiss Alerts (5 s) ---- */
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });


    /* ---- 3. Smooth Scroll for Anchor Links ---- */
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });


    /* ---- 4. Navbar Scroll Effect ---- */
    var navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }


    /* ---- 5. Animate Elements on Scroll (Intersection Observer) ---- */
    var observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(function (el) {
        observer.observe(el);
    });


    /* ---- 6. Profile Picture Preview ---- */
    var profilePicInput = document.querySelector('#id_profile_pic');
    var profilePicPreview = document.querySelector('#profile-pic-preview');

    if (profilePicInput && profilePicPreview) {
        profilePicInput.addEventListener('change', function (e) {
            var file = e.target.files[0];
            if (file) {
                // Basic client-side validation
                if (!file.type.startsWith('image/')) {
                    alert('Please select a valid image file.');
                    return;
                }
                if (file.size > 5 * 1024 * 1024) { // 5 MB limit
                    alert('Image must be smaller than 5 MB.');
                    profilePicInput.value = '';
                    return;
                }

                var reader = new FileReader();
                reader.onload = function (ev) {
                    profilePicPreview.src = ev.target.result;
                    profilePicPreview.style.display = 'block';

                    // Hide the letter-avatar placeholder if present
                    var placeholder = document.querySelector('#avatar-placeholder');
                    if (placeholder) {
                        placeholder.style.display = 'none';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }


    /* ---- 7. Bio Character Counter ---- */
    var bioField = document.querySelector('#id_bio');
    if (bioField) {
        var maxLen = parseInt(bioField.getAttribute('maxlength'), 10) || 500;
        var counter = document.createElement('small');
        counter.classList.add('text-muted', 'd-block', 'text-end', 'mt-1');
        counter.textContent = bioField.value.length + '/' + maxLen + ' characters';
        bioField.parentNode.appendChild(counter);

        bioField.addEventListener('input', function () {
            var len = bioField.value.length;
            counter.textContent = len + '/' + maxLen + ' characters';

            if (len > maxLen) {
                counter.classList.add('text-danger');
                counter.classList.remove('text-muted');
            } else {
                counter.classList.remove('text-danger');
                counter.classList.add('text-muted');
            }
        });
    }


    /* ---- 8. Page Entrance Animation ---- */
    var mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('animate-fadeInUp');
    }


    /* ---- 9. Back-to-Top (optional, progressive enhancement) ---- */
    var backToTop = document.querySelector('#back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 400) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        });

        backToTop.addEventListener('click', function (e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

});
