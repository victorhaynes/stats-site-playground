from django.core.management.base import BaseCommand
from wrs_api.models import Season, Region, Platform, Rank, Role, Item, Champion

class Command(BaseCommand):
    help = 'Seeds essential database records for Season, Region, and Platform'

    def handle(self, *args, **kwargs):

        # Create a season
        season, created = Season.objects.get_or_create(season=14, split=2)
        if created:
            self.stdout.write(self.style.SUCCESS('Season seeded successfully'))
        else:
            self.stdout.write(self.style.WARNING('A Season already exists, skipping seed...'))

        # Create regions
        americas, created = Region.objects.get_or_create(name='americas')
        if created:
            self.stdout.write(self.style.SUCCESS('Americas region seeded successfully'))
        else:
            self.stdout.write(self.style.WARNING('Americas region already exists, skipping seed...'))

        # Create regions
        asia, created = Region.objects.get_or_create(name='asia')
        if created:
            self.stdout.write(self.style.SUCCESS('Asia region seeded successfully'))
        else:
            self.stdout.write(self.style.WARNING('Asia region already exists, skipping seed...'))

        # Create regions
        europe, created = Region.objects.get_or_create(name='europe')
        if created:
            self.stdout.write(self.style.SUCCESS('Europe region seeded successfully'))
        else:
            self.stdout.write(self.style.WARNING('Europe region already exists, skipping seed...'))

        # Create regions
        sea, created = Region.objects.get_or_create(name='sea')
        if created:
            self.stdout.write(self.style.SUCCESS('SEA region seeded successfully'))
        else:
            self.stdout.write(self.style.WARNING('SEA region already exists, skipping seed...'))




        # Create na1 platform for Americas
        platform, created = Platform.objects.get_or_create(code='na1', region=americas)
        if created:
            self.stdout.write(self.style.SUCCESS('Platform "na1" seeded successfully'))
        else:
            self.stdout.write(self.style.WARNING('"na1" platform already exists, skipping seed...'))

        # Create br1 platform for Americas
        platform, created = Platform.objects.get_or_create(code='br1', region=americas)
        if created:
            self.stdout.write(self.style.SUCCESS('Platform "br1" seeded successfully'))
        else:
            self.stdout.write(self.style.WARNING('"br1" platform already exists, skipping seed...'))

        # Create euw1 platform for Americas
        platform, created = Platform.objects.get_or_create(code='euw1', region=europe)
        if created:
            self.stdout.write(self.style.SUCCESS('Platform "euw1" seeded successfully'))
        else:
            self.stdout.write(self.style.WARNING('"euw1" platform already exists, skipping seed...'))


        elo_values = [
            "Unranked",
            "Iron 4", "Iron 3", "Iron 2", "Iron 1",
            "Bronze 4", "Bronze 3", "Bronze 2", "Bronze 1",
            "Silver 4", "Silver 3", "Silver 2", "Silver 1",
            "Gold 4", "Gold 3", "Gold 2", "Gold 1",
            "Platinum 4", "Platinum 3", "Platinum 2", "Platinum 1",
            "Emerald 4", "Emerald 3", "Emerald 2", "Emerald 1",
            "Diamond 4", "Diamond 3", "Diamond 2", "Diamond 1",
            "Master", "Grandmaster", "Challenger"
        ]
        
        for elo_value in elo_values:
            rank, created = Rank.objects.get_or_create(elo=elo_value)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Rank "{elo_value}" seeded successfully'))
            else:
                self.stdout.write(self.style.WARNING(f'Rank "{elo_value}" already exists, skipping seed...'))


        role_values = [
            "TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"
        ]
        
        for role in role_values:
            position, created = Role.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Role "{role}" seeded successfully'))
            else:
                self.stdout.write(self.style.WARNING(f'Role "{role}" already exists, skipping seed...'))

        # Create dummy Champion for stats logic
