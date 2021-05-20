(function() {
    $(document).ajaxSend(function (event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                    (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                    !(/^(\/\/|http:|https:).*/.test(url));
        }

        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });

    $(function() {
        var helper;
        $("#id_searchname").focusin( function() {
            window.setTimeout( function() {
                if ($("#id_searchname").is(":focus")) {
                    if (helper == undefined) {
                        clippy.load('Clippy', function (agent) {
                            helper = agent;
                            helper.show();
                            helper.speak(django.gettext("Hi! I am Clippy, your Lagerregal assistant. Would you like some assistance totday?"));
                        });
                    }
                } else {
                    helper.animate();
                }
            }, 60000 );
        });

        $(document).on('change', '[data-autosubmit="change"] select', function(event) {
            this.form.submit();
        });

        $('[data-table]').dataTable();
        $('[data-timeago]').timeago();
        $('#id_duedate').datepicker();

        $(document).on('submit', 'form[data-confirm]', function(event) {
            var msg = $(this).data('confirm');
            if (!window.confirm(msg)) {
                event.preventDefault();
            }
        });
    });
})();
