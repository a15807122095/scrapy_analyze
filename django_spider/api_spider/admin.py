from django.contrib import admin

import sys,os
sys.path.append(os.path.dirname(__file__) + os.sep + '../')

# Register your models here.
from ..models import GamePythonMatch, GameMatchBattle, GamePlayerBattleRecord, GameBetInfoCopy, \
    GameLeagueBoard, GameLolHeroesLeagueStats, GameLolPlayerLeagueStats,\
    GameLolTeamLeagueStats, GameKogHeroesLeagueStats, GameKogPlayerLeagueStats, GameKogTeamLeagueStats


class GamePythonMatchAdmin(admin.ModelAdmin):
    list_display = ['type', 'league_id', 'status', 'start_time', 'bo', 'team_a_id', 'team_a_name', 'team_a_score'
    'team_b_id', 'team_b_name', 'team_b_score', 'league_name', 'win_team', 'source_from', 'source_matchid']
    list_filter = ('team_a_name', 'team_b_name', 'source_from')  # 过滤器 通过name字段筛选显示
admin.site.register(GamePythonMatch, GamePythonMatchAdmin)
admin.site.site_header = '游戏赛程表'
admin.site.site_title = '游戏赛程表'
