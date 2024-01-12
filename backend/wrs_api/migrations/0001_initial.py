# Generated by Django 4.2.7 on 2024-01-12 21:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.IntegerField()),
                ('split', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Summoner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puuid', models.CharField(max_length=100)),
                ('gameName', models.CharField(max_length=50)),
                ('tagLine', models.CharField(max_length=10)),
                ('region', models.CharField(max_length=40)),
                ('profile_icon_id', models.IntegerField(blank=True)),
                ('encrypted_summoner_id', models.CharField(max_length=100)),
                ('summonerName', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SummonerOverview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overview', models.JSONField(default=dict)),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wrs_api.season')),
                ('summoner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wrs_api.summoner')),
            ],
        ),
        migrations.CreateModel(
            name='MatchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('all_match_history', models.JSONField(default=list)),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wrs_api.season')),
                ('summoner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wrs_api.summoner')),
            ],
        ),
    ]
