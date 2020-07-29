from django.contrib import admin

import sys,os
sys.path.append(os.path.dirname(__file__) + os.sep + '../')

# Register your models here.

from .models import GamePythonMatch, GameMatchBattle, GamePlayerBattleRecord, GameBetInfoCopy, BlackList, \
    GameLeagueBoard, GameLolHeroesLeagueStats, GameLolPlayerLeagueStats, ApiCheck200,GamePlayerHeroStats, \
    GameLolTeamLeagueStats, GameKogHeroesLeagueStats, GameKogPlayerLeagueStats, GameKogTeamLeagueStats

# 赛程表admin
class GamePythonMatchAdmin(admin.ModelAdmin):
    list_display = ['type', 'league_id', 'status', 'start_time', 'bo', 'team_a_id', 'team_a_name', 'team_a_score',
    'team_b_id', 'team_b_name', 'team_b_score', 'league_name', 'win_team', 'source_from', 'source_matchid']
    list_filter = ('source_from',)


# 对局详情admin
class GameMatchBattleAdmin(admin.ModelAdmin):
    list_display = ['duration', 'economic_diff', 'status', 'type', 'team_a_kill_count', 'team_b_kill_count',
                    'team_a_death_count', 'team_b_death_count', 'team_a_assist_count', 'team_b_assist_count',
                    'team_a_big_dragon_count', 'team_b_big_dragon_count', 'team_a_small_dragon_count',
                    'team_b_small_dragon_count', 'team_a_tower_count', 'team_b_tower_count', 'win_team',
                    'first_big_dragon_team', 'first_small_dragon_team', 'first_blood_team', 'team_a_five_kills',
                    'team_b_five_kills', 'team_a_ten_kills', 'team_b_ten_kills', 'first_tower_team', 'team_a_money',
                    'team_b_money', 'team_a_hero', 'team_b_hero', 'team_a_side', 'team_b_side', 'match_id', 'index_num',
                    'source_matchid']
    list_filter = ('type',)


# 选手对局详情admin
class GamePlayerBattleRecordAdmin(admin.ModelAdmin):
    list_display = ['match_id', 'player_id', 'player_name', 'player_avatar', 'hero_id', 'hero_level',
                    'hero_name', 'hero_avatar', 'kill_count', 'death_count', 'assist_count', 'last_hit_count',
                    'last_hit_minute', 'damage_count', 'damage_minute', 'damage_percent', 'damage_taken_count',
                    'damage_taken_minute', 'damage_taken_percent', 'kda', 'money_count', 'money_minute', 'offered_rate',
                    'score', 'equip_ids', 'skill_ids', 'position', 'type', 'source_matchid', 'team_id']
    list_filter = ('type',)


# 赔率表admin
class GameBetInfoCopyAdmin(admin.ModelAdmin):
    list_display = ['type', 'source', 'source_matchid', 'match_stage', 'match_id', 'board_num', 'title', 'bet_type',
    'end_time', 'status', 'handicap', 'option_one_name', 'option_two_name', 'option_one_odds', 'option_two_odds',
    'option_one_team_id', 'option_two_team_id', 'win', 'source_status']
    list_filter = ('type', 'source', 'title', 'status', 'win')


# 英雄联盟英雄排行榜admin
class GameLolHeroesLeagueStatsAdmin(admin.ModelAdmin):
    list_display = ['hero_id', 'hero_avatar', 'hero_name', 'league_id', 'assist_average', 'death_average',
                    'kill_average', 'kda_average', 'pick_rate', 'ban_rate', 'win_rate', 'pick_count', 'ban_count',
                    'win_count', 'type', 'position']
    list_filter = ('league_id',)


# 英雄联盟选手排行榜admin
class GameLolPlayerLeagueStatsAdmin(admin.ModelAdmin):
    list_display = ['player_id', 'league_id', 'kda', 'mvp_count', 'play_count', 'win_count', 'offered_rate',
                    'kill_count', 'kill_average', 'assist_count', 'assist_average', 'death_count', 'death_average',
                    'economic_minute', 'hit_minute', 'damage_deal_minute', 'damage_deal_rate', 'damage_taken_minute',
                    'damage_taken_rate', 'last_hit_per_game', 'most_kill_per_games', 'most_death_per_games',
                    'most_assist_per_games', 'type', 'team_id', 'nick_name', 'avatar', 'position']
    list_filter = ('league_id',)


# 英雄联盟团队排行榜admin
class GameLolTeamLeagueStatsAdmin(admin.ModelAdmin):
    list_display = ['team_id', 'league_id', 'play_count', 'win_rate', 'time_average', 'death_average', 'kill_average',
                    'economic_minute', 'first_blood_rate', 'tower_fail_average', 'tower_success_average', 'kda',
                    'damage_average', 'big_dragon_rate', 'big_dragon_average', 'small_dragon_rate',
                    'small_dragon_average', 'first_tower_rate', 'damage_minute', 'hit_minute', 'economic_average',
                    'type', 'wards_placed_minute', 'wards_killed_minute']
    list_filter = ('league_id',)


# 王者荣耀英雄排行榜admin
class GameKogHeroesLeagueStatsAdmin(admin.ModelAdmin):
    list_display = ['hero_id', 'hero_avatar', 'hero_name', 'league_id', 'pick_count', 'total_kill', 'kda_average',
                    'kill_average', 'death_average', 'assist_average', 'win_rate', 'show_rate', 'ban_rate', 'type',
                    'position']
    list_filter = ('league_id',)


# 王者荣耀选手排行榜admin
class GameKogPlayerLeagueStatsAdmin(admin.ModelAdmin):
    list_display = ['player_id', 'league_id', 'win_count', 'lose_count', 'play_count', 'mvp_count', 'kda', 'kill_count',
    'kill_average', 'death_count', 'death_average', 'assist_count', 'assist_average', 'offered_rate', 'economic_minute',
    'hit_minute', 'wards_placed_minute', 'wards_killed_minute', 'damage_deal_rate', 'damage_deal_minute',
    'damage_taken_minute', 'type', 'team_id', 'nick_name', 'avatar', 'position']
    list_filter = ('league_id',)


# 王者荣耀团队排行榜admin
class GameKogTeamLeagueStatsAdmin(admin.ModelAdmin):
    list_display = ['team_id', 'league_id', 'win_count', 'lost_count', 'play_count', 'time_average', 'first_blood_rate',
    'small_dragon_rate', 'small_dragon_average', 'big_dragon_rate', 'big_dragon_average', 'tower_success_average',
    'tower_fail_average', 'kda', 'kill_average', 'death_average', 'assist_average', 'economic_average', 'economic_minute',
    'hit_minute', 'wards_placed_minute', 'wards_killed_minute', 'damage_average', 'damage_minute', 'score', 'type', 'win_rate']
    list_filter = ('league_id',)


# 团队积分榜admin
class GameLeagueBoardAdmin(admin.ModelAdmin):
    list_display = ['league_id', 'team_id', 'win_count', 'lost_count', 'score', 'type_name', 'stage', 'type',
                    'team_name']
    list_filter = ('league_id',)


# 选手擅长英雄admin
class GamePlayerHeroStatsAdmin(admin.ModelAdmin):
    list_display = ['hero_id', 'player_id', 'kda', 'kill_average', 'death_average', 'assist_average',
                    'score', 'win_count', 'play_count', 'win_rate', 'type', 'hero_avatar']
    list_filter = ('type',)


# 旧黑名单admin
class ApiCheck200Admin(admin.ModelAdmin):
    list_display = ['league_name', 'team_a_name', 'team_b_name', 'check_distinct']
    list_filter = ('league_name',)


# 新黑名单admin
class BlackListAdmin(admin.ModelAdmin):
    list_display = ['league_name', 'team_name', 'player_name', 'hero_name', 'source_from', 'judge_position']
    list_filter = ('league_name',)


admin.site.register(GamePythonMatch, GamePythonMatchAdmin)
admin.site.register(GameMatchBattle, GameMatchBattleAdmin)
admin.site.register(GamePlayerBattleRecord, GamePlayerBattleRecordAdmin)
admin.site.register(GameBetInfoCopy, GameBetInfoCopyAdmin)
admin.site.register(GameLolHeroesLeagueStats, GameLolHeroesLeagueStatsAdmin)
admin.site.register(GameLolPlayerLeagueStats, GameLolPlayerLeagueStatsAdmin)
admin.site.register(GameLolTeamLeagueStats, GameLolTeamLeagueStatsAdmin)
admin.site.register(GameKogHeroesLeagueStats, GameKogHeroesLeagueStatsAdmin)
admin.site.register(GameKogPlayerLeagueStats, GameKogPlayerLeagueStatsAdmin)
admin.site.register(GameKogTeamLeagueStats, GameKogTeamLeagueStatsAdmin)
admin.site.register(GameLeagueBoard, GameLeagueBoardAdmin)
admin.site.register(GamePlayerHeroStats, GamePlayerHeroStatsAdmin)
admin.site.register(ApiCheck200, ApiCheck200Admin)
admin.site.register(BlackList, BlackListAdmin)



admin.site.site_header = '游戏相关表'
admin.site.site_title = '游戏相关表'

