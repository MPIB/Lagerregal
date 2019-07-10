import random
import urllib
from os import makedirs
from os import path

from django.conf import settings  # import the settings file
from django.core.management.base import BaseCommand

from faker import Faker

from devicegroups.models import Devicegroup
from devices.models import Building
from devices.models import Device
from devices.models import Lending
from devices.models import Manufacturer
from devices.models import Picture
from devices.models import Room
from devicetypes.models import Type
from Lagerregal import utils
from locations.models import Section
from users.models import Department
from users.models import DepartmentUser
from users.models import Lageruser

fake = Faker('de_DE')


def fake_building(word):
    return Building(
        name=word.title(),
        street=fake.street_name(),
        number=fake.random.randint(1, 200),
        zipcode=fake.postcode(),
        city=fake.city(),
        state=fake.state(),
        country=fake.country()
    )


def fake_section(word):
    return Section(name=word.title())


def fake_room(word):
    return Room(
        name=word.title(),
        building=Building.objects.order_by('?').first(),
        section=Section.objects.order_by('?').first()
    )


def fake_manufacturer():
    return Manufacturer(name=fake.company())


def fake_department(word):
    return Department(name=word.title())


def fake_lageruser(word):
    return Lageruser(
        main_department=Department.objects.order_by('?').first(),
        username=word,
        first_name=fake.first_name(),
        last_name=fake.last_name()
    )


def fake_devicetype(word):
    return Type(name=word.title())


def fake_devicegroup(word):
    return Devicegroup(
        name=word.title(),
        department=Department.objects.order_by('?').first()
    )


def fake_device(inventorynumber, word):
    return Device(
        created_at=fake.past_date(start_date="-600d"),
        creator=Lageruser.objects.order_by('?').first(),
        name=word.title(),
        inventorynumber=inventorynumber,
        serialnumber=random.randint(1, 1000),
        manufacturer=Manufacturer.objects.order_by('?').first(),
        devicetype=Type.objects.order_by('?').first(),
        room=Room.objects.order_by('?').first(),
        group=Devicegroup.objects.order_by('?').first(),
        department=Department.objects.order_by('?').first()
    )


def fake_lending(device, user):
    lending = Lending(
        owner=user,
        lenddate=fake.date_between(start_date='-100d', end_date='-50d')
    )
    if random.randint(0, 100) > 75:
        lending.duedate = fake.future_date(end_date='+50d')
    else:
        lending.returndate = fake.date_between(start_date='-50d', end_date='today')
    if random.randint(0, 100) > 80:
        lending.smalldevice = fake.word()
    else:
        lending.device = device
    return lending


def generate_buildings(number):
    print("Generating buildings")
    word_list = fake.words(number, unique=True)
    Building.objects.bulk_create(fake_building(word) for word in word_list)


def generate_sections(number):
    print("Generating sections")
    word_list = fake.words(number, unique=True)
    Section.objects.bulk_create(fake_section(word) for word in word_list)


def generate_rooms(number):
    print("Generating rooms")
    word_list = fake.words(number, unique=True)
    Room.objects.bulk_create(fake_room(word) for word in word_list)


def generate_manufacturers(number):
    print("Generating manufacturers")
    Manufacturer.objects.bulk_create(fake_manufacturer() for i in range(number))


def generate_departments(number):
    print("Generating departments")
    word_list = fake.words(number, unique=True)
    Department.objects.bulk_create(fake_department(word) for word in word_list)


def generate_lagerusers(number):
    print("Generating lagerusers")
    word_list = fake.words(number, unique=True)
    Lageruser.objects.bulk_create(fake_lageruser(word) for word in word_list)


def generate_department_users():
    print("Generating departmentusers")
    users = Lageruser.objects.all()
    for user in users:
        if user.main_department:
            DepartmentUser.objects.create(user=user, department=user.main_department)


def generate_devicetypes(number):
    print("Generating devicetypes")
    word_list = fake.words(number, unique=True)
    Type.objects.bulk_create(fake_devicetype(word) for word in word_list)


def generate_devicegroups(number):
    print("Generating devicegroups")
    word_list = fake.words(number, unique=True)
    Devicegroup.objects.bulk_create(fake_devicegroup(word) for word in word_list)


def generate_devices(number):
    print("Generating devices")
    inventorynumber_list = random.sample(range(0, 5000), number)
    word_list = fake.words(number, unique=True)
    Device.objects.bulk_create(fake_device(inventorynumber_list[i], word_list[i]) for i in range(number))


def generate_lendings(number):
    print("Generating lendings")
    devices = random.sample(list(Device.objects.all()), number)
    users = random.sample(list(Lageruser.objects.all()), number)
    for i in range(number):
        lending = fake_lending(devices[i], users[i])
        lending.save()
        if lending.device:
            devices[i].currentlending = lending
            devices[i].save()


def generate_pictures(number):
    """
    Every device gets one picture, but we only download a few unique images and
    recycle after that. Try to be as dynamic as possible and share state through
    settings.PRODUCTION with get_file_location so we do not get a uuid
    every time we save a fake image.
    """
    print("Generating pictures")
    devices = Device.objects.all()
    img_root = path.join(settings.MEDIA_ROOT, utils.get_file_location(Picture()))
    for i in range(number):
        img_path = path.join(img_root, 'dev_{:03}.png'.format(i))
        if not path.exists(img_path):
            makedirs(path.dirname(img_path), exist_ok=True)
            urllib.request.urlretrieve("https://lorempixel.com/640/480/technics", img_path)
    for index, device in enumerate(devices):
        pic = Picture(device=device)
        # recycle images after <number> uses
        pic.image = utils.get_file_location(pic, 'dev_{:03}.png'.format(index % number))
        pic.save()


class Command(BaseCommand):
    help = 'Populate database with sample data.'
    err = SystemExit("can't create sample data in production mode")
    try:
        if settings.PRODUCTION:
            raise err
    except AttributeError:
        raise err

    def handle(self, *args, **options):
        if Building.objects.exists():
            print("It looks like your database already contains objects. Skipping…")
        else:
            generate_buildings(20)
            generate_sections(20)
            generate_rooms(20)
            generate_manufacturers(5)
            generate_departments(5)
            generate_lagerusers(50)
            generate_department_users()
            generate_devicetypes(10)
            generate_devicegroups(10)
            generate_devices(150)
            generate_lendings(30)
            generate_pictures(20)
            admin = Lageruser.objects.create_superuser('admin', 'admin@localhost', 'admin')
            for department in Department.objects.all():
                DepartmentUser.objects.create(user=admin, department=department)
