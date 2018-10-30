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

    var helper;
    $(document).ready(function() {
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

        var getFilterBasePath = function() {
            var index = window.location.pathname.length;
            ['department', 'sorting', 'group', 'filter', 'page'].forEach(function(key) {
                var i = window.location.pathname.indexOf(key)
                if (i !== -1 && i < index) {
                    index = i;
                }
            });
            return window.location.pathname.substr(0, index - 1);
        };

        var getFilterPath = function() {
            var ids = {
                department: ["#id_departmentfilter"],
                sorting: ["#id_viewsorting"],
                group: ["#id_groupfilter"],
                filter: ["#id_viewfilter", "#id_filterstring"],
            };
            var defaults = {
                department: "all",
            };

            var path = '';
            var index = window.location.pathname.length;
            ['department', 'sorting', 'group', 'filter'].forEach(function(key) {
                ids[key].forEach(function(id) {
                    var element = $(id);
                    if (element.length) {
                        var value = element.val() || defaults[key];
                        path += "/" + key + "/" + value;
                    }
                });
            });

            return path;
        };

        var setFilters = function() {
            window.location.pathname = getFilterBasePath() + getFilterPath();
        };

        $('#id_departmentfilter').change(setFilters);
        $('#id_viewsorting').change(setFilters);
        $('#id_groupfilter').change(setFilters);
        $('#id_viewfilter').change(setFilters);
        $('#id_filterstring').change(setFilters);
        $(".pageselect").change(function() {
            var s = "/page/" + $(this).val();
            window.location.pathname = getFilterBasePath() + s + getFilterPath();
        });

        $('[data-timeago]').timeago();
        $('[data-toggle="popover"]').popover();
        $('#id_duedate').datepicker();
    });
})();
