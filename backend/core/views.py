import logging

from django.shortcuts import render

logger = logging.getLogger(__name__)


def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request):
    logger.exception("Internal server error")
    return render(request, "500.html", status=500)
