import json

from django.db.models import Max
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic.base import View

from main.models import WIDGETS
from main.models import DashboardWidget
from main.views import get_widget_data


class WidgetAdd(View):
    def post(self, request):
        widgetname = request.POST["widgetname"]
        if widgetname in dict(WIDGETS):
            userwidgets = DashboardWidget.objects.filter(user=request.user)
            if len(userwidgets.filter(widgetname=widgetname)) != 0:
                return HttpResponse("")
            widget = DashboardWidget()
            widget.column = "l"
            oldindex = userwidgets.filter(column="l").aggregate(Max('index'))["index__max"]
            widget.index = oldindex + 1 if oldindex is not None else 1
            widget.widgetname = widgetname
            widget.user = request.user
            widget.save()
            context = get_widget_data(request.user, [widgetname, ])
            context["hidecontrols"] = True
            return HttpResponse(render_to_string('snippets/widgets/{0}.html'.format(widgetname), context))
        else:
            return HttpResponse("Error: invalid widget name")


class WidgetRemove(View):
    def post(self, request):
        widgetname = request.POST["widgetname"]
        if widgetname in dict(WIDGETS):
            DashboardWidget.objects.get(user=request.user, widgetname=widgetname).delete()
            return HttpResponse("")
        else:
            return HttpResponse("Error: invalid widget name")


class WidgetToggle(View):
    def post(self, request):
        widgetname = request.POST["widgetname"]
        if widgetname in dict(WIDGETS):
            w = DashboardWidget.objects.get(user=request.user, widgetname=widgetname)
            w.minimized = not w.minimized
            w.save()
            return HttpResponse("")
        else:
            return HttpResponse("Error: invalid widget name")


class WidgetMove(View):
    def post(self, request):
        userwidgets = json.loads(request.POST["widgets"])

        for widgetname, widgetattr in userwidgets.items():
            if widgetname in dict(WIDGETS):
                w = DashboardWidget.objects.get(user=request.user, widgetname=widgetname)
                if w.index != widgetattr["index"] or w.column != widgetattr["column"]:
                    w.index = widgetattr["index"]
                    w.column = widgetattr["column"]
                    w.save()
        return HttpResponse("")
