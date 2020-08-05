# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ApiCheck200(models.Model):
    league_name = models.CharField(max_length=20, blank=True, null=True)
    team_a_name = models.CharField(max_length=50, blank=True, null=True)
    team_b_name = models.CharField(max_length=50, blank=True, null=True)
    check_distinct = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'api_check_200'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BlackList(models.Model):
    league_name = models.CharField(max_length=25, blank=True, null=True)
    team_name = models.CharField(max_length=25, blank=True, null=True)
    player_name = models.CharField(max_length=25, blank=True, null=True)
    hero_name = models.CharField(max_length=25, blank=True, null=True)
    source_from = models.IntegerField(blank=True, null=True)
    judge_position = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'black_list'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class GameBetInfoCopy(models.Model):
    type = models.IntegerField(blank=True, null=True)
    source = models.CharField(max_length=50, blank=True, null=True)
    source_matchid = models.CharField(max_length=50, blank=True, null=True)
    match_stage = models.CharField(max_length=50, blank=True, null=True)
    match_id = models.IntegerField(blank=True, null=True)
    board_num = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=120, blank=True, null=True)
    bet_type = models.IntegerField(blank=True, null=True)
    end_time = models.BigIntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    handicap = models.CharField(max_length=20, blank=True, null=True)
    option_one_name = models.CharField(max_length=100, blank=True, null=True)
    option_two_name = models.CharField(max_length=100, blank=True, null=True)
    option_one_odds = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    option_two_odds = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    option_one_team_id = models.CharField(max_length=15, blank=True, null=True)
    option_two_team_id = models.CharField(max_length=15, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    win = models.IntegerField(blank=True, null=True)
    source_status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_bet_info_copy'
        unique_together = (('source_matchid', 'title', 'match_stage'),)


class GameKogHeroesLeagueStats(models.Model):
    hero_id = models.IntegerField(blank=True, null=True)
    hero_avatar = models.CharField(max_length=255, blank=True, null=True)
    hero_name = models.CharField(max_length=50, blank=True, null=True)
    league_id = models.CharField(max_length=15, blank=True, null=True)
    pick_count = models.IntegerField(blank=True, null=True)
    total_kill = models.IntegerField(blank=True, null=True)
    kda_average = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    kill_average = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    death_average = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    assist_average = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ban_count = models.IntegerField(blank=True, null=True)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    show_rate = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ban_rate = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    position = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_kog_heroes_league_stats'
        unique_together = (('league_id', 'hero_id'),)


class GameKogPlayerLeagueStats(models.Model):
    player_id = models.CharField(max_length=15, blank=True, null=True)
    league_id = models.CharField(max_length=15, blank=True, null=True)
    win_count = models.IntegerField(blank=True, null=True)
    lose_count = models.IntegerField(blank=True, null=True)
    play_count = models.IntegerField(blank=True, null=True)
    mvp_count = models.IntegerField(blank=True, null=True)
    kda = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    kill_count = models.IntegerField(blank=True, null=True)
    kill_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    death_count = models.IntegerField(blank=True, null=True)
    death_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    assist_count = models.IntegerField(blank=True, null=True)
    assist_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    offered_rate = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    economic_minute = models.DecimalField(max_digits=8, decimal_places=1, blank=True, null=True)
    hit_minute = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    wards_placed_minute = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    wards_killed_minute = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    damage_deal_rate = models.DecimalField(max_digits=8, decimal_places=1, blank=True, null=True)
    damage_deal_minute = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    damage_taken_minute = models.DecimalField(max_digits=9, decimal_places=1, blank=True, null=True)
    damage_taken_rate = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    team_id = models.CharField(max_length=15, blank=True, null=True)
    nick_name = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_kog_player_league_stats'
        unique_together = (('league_id', 'player_id'),)


class GameKogTeamLeagueStats(models.Model):
    team_id = models.CharField(max_length=15, blank=True, null=True)
    league_id = models.CharField(max_length=15, blank=True, null=True)
    win_count = models.IntegerField(blank=True, null=True)
    lost_count = models.IntegerField(blank=True, null=True)
    play_count = models.IntegerField(blank=True, null=True)
    time_average = models.IntegerField(blank=True, null=True)
    first_blood_rate = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    small_dragon_rate = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    small_dragon_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    big_dragon_rate = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    big_dragon_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    tower_success_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    tower_fail_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    kda = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    kill_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    death_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    assist_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    economic_average = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    economic_minute = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    hit_minute = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    wards_placed_minute = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    wards_killed_minute = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    damage_average = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    damage_minute = models.DecimalField(max_digits=9, decimal_places=1, blank=True, null=True)
    score = models.DecimalField(max_digits=7, decimal_places=1, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    win_rate = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_kog_team_league_stats'
        unique_together = (('league_id', 'team_id'),)


class GameLeagueBoard(models.Model):
    league_id = models.CharField(max_length=15, blank=True, null=True)
    team_id = models.CharField(max_length=15, blank=True, null=True)
    win_count = models.IntegerField(blank=True, null=True)
    lost_count = models.IntegerField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    type_name = models.CharField(max_length=50, blank=True, null=True)
    stage = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    team_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_league_board'
        unique_together = (('league_id', 'team_id', 'stage'),)


class GameLolHeroesLeagueStats(models.Model):
    hero_id = models.IntegerField(blank=True, null=True)
    hero_avatar = models.CharField(max_length=255, blank=True, null=True)
    hero_name = models.CharField(max_length=50, blank=True, null=True)
    league_id = models.CharField(max_length=15, blank=True, null=True)
    assist_average = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    death_average = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    kill_average = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    kda_average = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    pick_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ban_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    pick_count = models.IntegerField(blank=True, null=True)
    ban_count = models.IntegerField(blank=True, null=True)
    win_count = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    position = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_lol_heroes_league_stats'
        unique_together = (('league_id', 'hero_id'),)


class GameLolPlayerLeagueStats(models.Model):
    player_id = models.CharField(max_length=15, blank=True, null=True)
    league_id = models.CharField(max_length=15, blank=True, null=True)
    kda = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    mvp_count = models.IntegerField(blank=True, null=True)
    play_count = models.IntegerField(blank=True, null=True)
    win_count = models.IntegerField(blank=True, null=True)
    offered_rate = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    kill_count = models.IntegerField(blank=True, null=True)
    kill_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    assist_count = models.IntegerField(blank=True, null=True)
    assist_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    death_count = models.IntegerField(blank=True, null=True)
    death_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    economic_minute = models.DecimalField(max_digits=8, decimal_places=1, blank=True, null=True)
    hit_minute = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    damage_deal_minute = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    damage_deal_rate = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    damage_taken_minute = models.DecimalField(max_digits=9, decimal_places=1, blank=True, null=True)
    damage_taken_rate = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    last_hit_per_game = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    most_kill_per_games = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    most_death_per_games = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    most_assist_per_games = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    team_id = models.CharField(max_length=15, blank=True, null=True)
    nick_name = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_lol_player_league_stats'
        unique_together = (('league_id', 'player_id'),)


class GameLolTeamLeagueStats(models.Model):
    team_id = models.CharField(max_length=15, blank=True, null=True)
    league_id = models.CharField(max_length=15, blank=True, null=True)
    play_count = models.IntegerField(blank=True, null=True)
    win_rate = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    time_average = models.IntegerField(blank=True, null=True)
    death_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    kill_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    economic_minute = models.DecimalField(max_digits=9, decimal_places=1, blank=True, null=True)
    first_blood_rate = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    tower_fail_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    tower_success_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    kda = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    damage_average = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    big_dragon_rate = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    big_dragon_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    small_dragon_rate = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    small_dragon_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    first_tower_rate = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    damage_minute = models.DecimalField(max_digits=9, decimal_places=1, blank=True, null=True)
    hit_minute = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    economic_average = models.DecimalField(max_digits=9, decimal_places=1, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    wards_placed_minute = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    wards_killed_minute = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    assist_average = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_lol_team_league_stats'
        unique_together = (('league_id', 'team_id'),)


class GameMatchBattle(models.Model):
    duration = models.IntegerField(blank=True, null=True)
    economic_diff = models.TextField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    team_a_kill_count = models.IntegerField(blank=True, null=True)
    team_b_kill_count = models.IntegerField(blank=True, null=True)
    team_a_death_count = models.IntegerField(blank=True, null=True)
    team_b_death_count = models.IntegerField(blank=True, null=True)
    team_a_assist_count = models.IntegerField(blank=True, null=True)
    team_b_assist_count = models.IntegerField(blank=True, null=True)
    team_a_big_dragon_count = models.IntegerField(blank=True, null=True)
    team_b_big_dragon_count = models.IntegerField(blank=True, null=True)
    team_a_small_dragon_count = models.IntegerField(blank=True, null=True)
    team_b_small_dragon_count = models.IntegerField(blank=True, null=True)
    team_a_tower_count = models.IntegerField(blank=True, null=True)
    team_b_tower_count = models.IntegerField(blank=True, null=True)
    win_team = models.CharField(max_length=1, blank=True, null=True)
    first_big_dragon_team = models.CharField(max_length=1, blank=True, null=True)
    first_small_dragon_team = models.CharField(max_length=1, blank=True, null=True)
    first_blood_team = models.CharField(max_length=1, blank=True, null=True)
    team_a_five_kills = models.CharField(max_length=1, blank=True, null=True)
    team_b_five_kills = models.CharField(max_length=1, blank=True, null=True)
    team_a_ten_kills = models.CharField(max_length=1, blank=True, null=True)
    team_b_ten_kills = models.CharField(max_length=1, blank=True, null=True)
    first_tower_team = models.CharField(max_length=1, blank=True, null=True)
    team_a_money = models.IntegerField(blank=True, null=True)
    team_b_money = models.IntegerField(blank=True, null=True)
    team_a_hero = models.TextField(blank=True, null=True)
    team_b_hero = models.TextField(blank=True, null=True)
    team_a_side = models.CharField(max_length=6, blank=True, null=True)
    team_b_side = models.CharField(max_length=6, blank=True, null=True)
    match_id = models.IntegerField(blank=True, null=True)
    index_num = models.IntegerField(blank=True, null=True)
    source_matchid = models.CharField(unique=True, max_length=50, blank=True, null=True)
    source_from = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_match_battle'


class GamePlayerBattleRecord(models.Model):
    match_id = models.IntegerField(blank=True, null=True)
    player_id = models.CharField(max_length=15, blank=True, null=True)
    player_name = models.CharField(max_length=50, blank=True, null=True)
    player_avatar = models.CharField(max_length=255, blank=True, null=True)
    hero_id = models.IntegerField(blank=True, null=True)
    hero_level = models.IntegerField(blank=True, null=True)
    hero_name = models.CharField(max_length=10, blank=True, null=True)
    hero_avatar = models.CharField(max_length=255, blank=True, null=True)
    kill_count = models.IntegerField(blank=True, null=True)
    death_count = models.IntegerField(blank=True, null=True)
    assist_count = models.IntegerField(blank=True, null=True)
    last_hit_count = models.IntegerField(blank=True, null=True)
    last_hit_minute = models.IntegerField(blank=True, null=True)
    damage_count = models.IntegerField(blank=True, null=True)
    damage_minute = models.IntegerField(blank=True, null=True)
    damage_percent = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    damage_taken_count = models.IntegerField(blank=True, null=True)
    damage_taken_minute = models.IntegerField(blank=True, null=True)
    damage_taken_percent = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    kda = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    money_count = models.IntegerField(blank=True, null=True)
    money_minute = models.IntegerField(blank=True, null=True)
    offered_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    equip_ids = models.TextField(blank=True, null=True)
    skill_ids = models.TextField(blank=True, null=True)
    position = models.CharField(max_length=20, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    source_matchid = models.CharField(max_length=50, blank=True, null=True)
    team_id = models.CharField(max_length=20, blank=True, null=True)
    source_from = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_player_battle_record'
        unique_together = (('source_matchid', 'player_id'),)


class GamePlayerHeroStats(models.Model):
    hero_id = models.IntegerField(blank=True, null=True)
    player_id = models.CharField(max_length=15, blank=True, null=True)
    kda = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    kill_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    death_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    assist_average = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    score = models.DecimalField(max_digits=9, decimal_places=1, blank=True, null=True)
    win_count = models.IntegerField(blank=True, null=True)
    play_count = models.IntegerField(blank=True, null=True)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    hero_avatar = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_player_hero_stats'


class GamePythonMatch(models.Model):
    type = models.IntegerField(blank=True, null=True)
    league_id = models.CharField(max_length=15, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    start_time = models.BigIntegerField(blank=True, null=True)
    bo = models.IntegerField(blank=True, null=True)
    team_a_id = models.CharField(max_length=15, blank=True, null=True)
    team_a_name = models.CharField(max_length=50, blank=True, null=True)
    team_a_score = models.IntegerField(blank=True, null=True)
    team_b_id = models.CharField(max_length=15, blank=True, null=True)
    team_b_name = models.CharField(max_length=50, blank=True, null=True)
    team_b_score = models.IntegerField(blank=True, null=True)
    league_name = models.CharField(max_length=20, blank=True, null=True)
    win_team = models.CharField(max_length=4, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    propertys = models.CharField(max_length=30, blank=True, null=True)
    check_match = models.CharField(max_length=100, blank=True, null=True)
    source_from = models.CharField(max_length=50, blank=True, null=True)
    source_matchid = models.CharField(db_column='source_matchId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bet_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_python_match'
        unique_together = (('source_from', 'source_matchid'),)
