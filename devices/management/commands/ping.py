import subprocess
from network.models import IpAddress
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        for ip in IpAddress.objects.all()[:50]:
            res = subprocess.call(['ping', '-c', '1', '-t', '5', ip.address])
            if res == 0:
                print "ping to", ip, "OK"
            elif res == 2:
                print "no response from", ip
            else:
                print "ping to", ip, "failed!"