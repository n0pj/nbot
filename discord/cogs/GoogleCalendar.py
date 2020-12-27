from __future__ import print_function

from discord.ext import commands
from datetime import datetime
from dateutil import parser
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleCalendar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command()
    async def what(self, ctx, what: int):
        await ctx.send(f'{what}???')

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if(message.author.bot):
    #         return

    #     if(message):
    #         await message.channel.send(message)
    #         print(message)

    @commands.command()
    async def start(self, ctx):
        return await ctx.send('started')

    @commands.command()
    async def exit(self, ctx):
        return await ctx.send('exited')

    @commands.command()
    async def test_method(self, ctx, arg):
        return await ctx.send(arg)

    @commands.command()
    async def setup_calendar(self, ctx, *args):
        scopes = ['https://www.googleapis.com/auth/calendar']
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refrestoken:
                # await ctx.send(Request)
                # await ctx.send('request')

                creds.refresh(Request)
            else:
                # await ctx.send('flow')

                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    scopes,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )
                auth_url, _ = flow.authorization_url(prompt='consent')

                # creds = flow.run_local_server()
                print('Please go to this URL: {}'.format(auth_url))
                await ctx.send('このURL でコードを発行したら、/auth を実行してね。')
                await ctx.send(auth_url)
                # creds = flow.run_local_server(port=0)
                # await ctx.send('flow')
                self.flow = flow

    @commands.command()
    async def auth(self, ctx, code):
        # If modifying these scopes, delete the file token.pickle.
        user_id = ctx.author.id
        flow = self.flow
        # auth_url, _ = flow.authorization_url(prompt='consent')
        # creds = flow.run_local_server()
        # credentials = flow.run_console()
        flow.fetch_token(code=code)
        # print('Please go to this URL: {}'.format(auth_url))
        # print(credentials)

        # await ctx.send(auth_url)
        # creds = flow.run_local_server(port=0)
        creds = flow.credentials

        # await ctx.send('flow')

        with open('pickles/{}token.pickle'.format(user_id), 'wb') as token:
            pickle.dump(creds, token)

        service = build('people', 'v1', credentials=creds)

        # Call the People API
        print('List 10 connection names')
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=10,
            personFields='names,emailAddresses').execute()
        connections = results.get('connections', [])

        for person in connections:
            names = person.get('names', [])
            if names:
                name = names[0].get('displayName')
                print(name)
        await ctx.send('Google Calendar が使用可能になったよ。')

    @commands.command()
    async def read(self, ctx):
        pickle_file = 'pickles/{}token.pickle'.format(ctx.author.id)
        creds = None

        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as token:
                creds = pickle.load(token)
        else:
            await ctx.send('イベントを取得できなかった')
            return

        service = build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print('Getting the upcoming 10 events')
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    @commands.command()
    async def create(self, ctx, *event_data):
        pickle_file = 'pickles/{}token.pickle'.format(ctx.author.id)
        creds = None

        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as token:
                creds = pickle.load(token)
        else:
            return await ctx.send('setup が完了していないから /setup_calendar を実行してね。')

        service = build('calendar', 'v3', credentials=creds)
        # start, end: require, summary: require, description: option

        count_event_data = len(event_data)
        if(count_event_data <= 2):
            return await ctx.send('必要なデータが足りていないよ。')
        start = event_data[0]
        # start = datetime.fromisoformat(start).isoformat()
        try:
            start = parser.parse(start).isoformat()
        except Exception:
            return ctx.send('書式がおかしいよ。')

        end = event_data[1]
        # end = datetime.datetime(end).isoformat()
        try:
            end = parser.parse(end).isoformat()
        except Exception:
            return ctx.send('書式がおかしいよ。')

        summary = event_data[2]

        description = ''
        try:
            description = event_data[3]
        except Exception:
            pass

        event = {
            'summary': summary,
            # 'location': 'Shibuya Office',
            'description': description,
            'start': {
                'dateTime': start,
                'timeZone': 'Japan',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'Japan',
            },
        }
        try:
            event = service.events().insert(calendarId='primary',
                                            body=event).execute()
            # print(event['id'])
            return await ctx.send('イベントを登録したよ。')
        except Exception:
            # print(Exception)
            return await ctx.send('イベントを登録できなかった。書式は正しい？それかネットワークのエラーかもしれない。')


def setup(bot):
    bot.add_cog(GoogleCalendar(bot))
