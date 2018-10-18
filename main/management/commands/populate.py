from django.conf import settings  # import the settings file
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from faker import Faker
import random
import urllib

from Lagerregal import utils
from devices.models import Building, Room, Manufacturer, Device, Picture, Lending
from devicegroups.models import Devicegroup
from devicetypes.models import Type
from locations.models import Section
from users.models import Lageruser, Department, DepartmentUser

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
        lending.due_date = fake.future_date(end_date='+50d')
    else:
        lending.return_date = fake.date_between(start_date='-50d', end_date='today')
    if random.randint(0, 100) > 80:
        lending.smalldevice = fake.word()
    else:
        lending.smalldevice = device
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
    Lending.objects.bulk_create(fake_lending(devices[i], users[i]) for i in range(number))


# every device gets a picture, but we only download a few unique images
def generate_pictures(number):
    print("Generating pictures")
    devices = Device.objects.all()
    picture_pool = []
    for i in range(number):
        with urllib.request.urlopen("https://lorempixel.com/640/480/technics") as r:
            picture_pool.append(r.read())
    for index, device in enumerate(devices):
        pic = Picture(device=device)
        pic.image.save(utils.get_file_location() + 'jpg',
            ContentFile(picture_pool[index % number]))


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
            raise SystemExit("It looks like your database already contains objects")
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
            Lageruser.objects.create_superuser('admin', 'admin@localhost', 'admin')
