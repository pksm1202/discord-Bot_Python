import discord
from discord.ext import commands
import random
from google_images_search import GoogleImagesSearch
import openai

# 봇 설정
bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())


gis = GoogleImagesSearch('구글 이미지 서치 키')
# OpenAI API 키
OPENAI_API_KEY = '오픈 AI 키'

# OpenAI 엔진 및 모델 설정
openai.api_key = OPENAI_API_KEY
openai_engine = "gpt-3.5-turbo"




# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    print(f'온라인 {bot.user.name}')

# 랜덤으로 항목 선택하는 명령어
@bot.command(name='랜덤', help='랜덤으로 입력한 값을 정해줌. \n\n 사용법: !랜덤 [ 항목1 항목2 항목3... ]')
async def random_pick(ctx, *args):
    # 입력된 항목이 없으면 에러 메시지 출력
    if not args:
        await ctx.send('사용법: !랜덤 [ 항목1 항목2 항목3... ]')
        return

    # 리스트에서 랜덤으로 하나를 선택
    selected_item = random.choice(args)

    # 선택된 항목을 출력
    await ctx.send(f'랜덤으로 선택된 항목: {selected_item}')

# !clear 명령어로 최근 메시지 삭제
@bot.command(name='삭제', help='사용자가 보낸 메세지를 삭제해줌. \n\n 사용법: !삭제 [ 자우고 싶은 갯수 ]')
async def clear_messages(ctx, amount: int = 5):
    # amount가 100보다 크면 100으로 설정
    amount = min(amount, 100)

    # 14일 이전의 메시지만 가져오기
    messages = []
    async for message in ctx.channel.history(limit=amount + 1):
        messages.append(message)

    # 메시지 삭제
    for message in messages:
        await message.delete()

@bot.command(name='움짤', help='구글에서 검색결과를 가져와 보여줌. \n\n 사용법: !움짤 [ 찾고싶은 이미지 ]')
async def send_gif(ctx, *args):
    search_query = ' '.join(args)
    
    # Google 이미지 검색
    gis.search(search_params={'q': search_query, 'num': 1})
    
    # 결과 확인 후 이미지 URL 가져오기
    if gis.results():
        result = gis.results()[0]
        gif_url = result.url
    else:
        gif_url = '검색결과가 없습니다'

    await ctx.send(gif_url)




        
# !질문 명령어 정의
@bot.command(name='질문', help='질문을 하면 AI가 답해줌. \n\n사용법: !질문 [ 질문 할 거 ] \n주의 ( AI의 지식이 2022년까지라 최신정보는 모름)')
async def ask_question(ctx, *, question):
    try:
        # OpenAI로 질문에 대한 답 생성
        response = openai.ChatCompletion.create(
            model=openai_engine,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Question: {question}"},
            ]
        )

        # OpenAI 응답에서 모든 답을 추출
        answers = [choice['message']['content'].strip() for choice in response['choices']]

        # 디스코드에 봇의 이름과 함께 모든 답 전송
        for answer in answers:
            # 길이가 1024자를 초과하는 경우 일부만 사용
            truncated_answer = answer[:1020] + '...' if len(answer) > 1024 else answer

            embed = discord.Embed(color=0xec1313)
            embed.add_field(name='', value=truncated_answer, inline=True)
            await ctx.send(embed=embed)

    except Exception as e:
        print(f"오류 발생: {e}")
        await ctx.send("죄송합니다. 현재 답변을 생성할 수 없습니다.")




# 제외할 명령어
excluded_commands = ['help', '명령어']

@bot.command(name='명령어')
async def show_commands(ctx):
    commands_list = [cmd for cmd in bot.commands if cmd.name not in ['help', '명령어']]

    command_info = []
    for cmd in commands_list:
        command_info.append(f'\n **{cmd.name}** : \n `{cmd.help or "도움말이 없습니다."} `')

    command_list_text = '\n'.join(command_info)

    embed = discord.Embed(color=0xec1313)
    embed.add_field(name='명령어 ', value=command_list_text, inline=True)
    await ctx.send(embed=embed)



# 봇 토큰 입력
bot.run('디스코드 봇 토큰')
