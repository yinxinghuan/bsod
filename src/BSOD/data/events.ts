import type { StoryEvent, StreamEvent } from '../types';

// ── Story Events ─────────────────────────────────────────────────────────────
// Triggered at phase start on specific days.

export const STORY_EVENTS: StoryEvent[] = [
  {
    id: 'day1_morning',
    day: 1,
    phase: 'morning',
    textZh: '第一天。父母昨天还在问你什么时候找一份"正经工作"。\n\n你打开电脑，看着空空的直播间。开播按钮就在那里。',
    textEn: 'Day one. Your parents asked yesterday when you\'d get a "real job".\n\nYou open your laptop and look at the empty streaming room. The start button is right there.',
    laisaEmotion: 'normal',
    choices: [
      {
        labelZh: '不管了，就是要做',
        labelEn: 'Screw it, I\'m doing this',
        effect: { mood: 10, focus: 5, connection: 0 },
        emotion: 'normal',
      },
      {
        labelZh: '……先想想看',
        labelEn: '...let me think about this',
        effect: { mood: -5, focus: 10 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 'day2_evening',
    day: 2,
    phase: 'evening',
    textZh: '昨天直播结束，一条弹幕说："主播真的超努力的！"\n\n就这么一条，让你回想了好久。',
    textEn: 'After yesterday\'s stream, one viewer said: "Streamer, you\'re really trying hard!"\n\nJust that one comment. You\'ve been thinking about it since.',
    laisaEmotion: 'happy',
    choices: [
      {
        labelZh: '把它截图存下来',
        labelEn: 'Screenshot it and save it',
        effect: { mood: 15, connection: 1 },
        emotion: 'happy',
      },
      {
        labelZh: '只是随便说说的吧',
        labelEn: 'They were probably just being nice',
        effect: { mood: 5 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 'day3_afternoon',
    day: 3,
    phase: 'afternoon',
    textZh: '手机震了一下。是初中同学：\n"最近在干嘛？听说你在做主播？真的假的哈哈"',
    textEn: 'Your phone buzzes. An old classmate:\n"Hey what are you up to? I heard you\'re a streamer lol is that real?"',
    laisaEmotion: 'surprised',
    choices: [
      {
        labelZh: '认真回复，说是的',
        labelEn: 'Reply honestly — yeah, I am',
        effect: { mood: 15, connection: 2 },
        emotion: 'happy',
      },
      {
        labelZh: '随手应付，"哈哈差不多"',
        labelEn: 'Brush it off — "haha kind of"',
        effect: { mood: 5 },
        emotion: 'normal',
      },
      {
        labelZh: '不回了',
        labelEn: 'Leave it on read',
        effect: { mood: -8, connection: -1 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 'day4_morning',
    day: 4,
    phase: 'morning',
    textZh: '黑猫跳上桌，挡住了屏幕。\n\n你把它移开，它又回来了。',
    textEn: 'The black cat jumps onto your desk and blocks the screen.\n\nYou move it. It comes back.',
    laisaEmotion: 'happy',
    choices: [
      {
        labelZh: '那就陪它玩一会儿',
        labelEn: 'Fine, play with it for a bit',
        effect: { mood: 18, energy: -5 },
        emotion: 'happy',
      },
      {
        labelZh: '拍张照片，继续开工',
        labelEn: 'Take a photo, then get back to work',
        effect: { mood: 10, followers: 25 },
        emotion: 'happy',
      },
    ],
  },
  {
    id: 'day5_evening',
    day: 5,
    phase: 'evening',
    textZh: '弹幕突然开始刷：\n"破千了！！" "恭喜Laisa！" "1000人在线"\n\n你看着那个数字，愣了三秒。',
    textEn: 'The chat explodes:\n"1000 viewers!!" "Congrats Laisa!" "We hit 1000 online"\n\nYou stare at that number for three seconds.',
    laisaEmotion: 'surprised',
    choices: [
      {
        labelZh: '大声庆祝，谢谢大家',
        labelEn: 'Celebrate out loud, thank everyone',
        effect: { mood: 25, followers: 60, connection: 1 },
        emotion: 'happy',
      },
      {
        labelZh: '装作淡定，继续打游戏',
        labelEn: 'Stay calm, keep playing',
        effect: { mood: 12, followers: 25 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 'day6_night',
    day: 6,
    phase: 'night',
    textZh: '你发现自己上一次看窗外是什么时候？\n\n想了想，大概是三天前。直播间的灯光比窗外的天更亮了。',
    textEn: 'When did you last look out the window?\n\nYou think about it. Three days ago, maybe. The stream lights are brighter than the sky outside.',
    laisaEmotion: 'sad',
    // No choices — reflective moment
  },
  {
    id: 'day7_morning',
    day: 7,
    phase: 'morning',
    textZh: '第七天。你翻出当初决定做主播时记的笔记。\n\n"我想让更多人觉得，有人和他们一起。"\n\n这句话写得很拙，但是当时你是认真的。',
    textEn: 'Day seven. You find the notes you wrote when you decided to start streaming.\n\n"I want more people to feel like someone\'s with them."\n\nBadly worded, but you meant it.',
    laisaEmotion: 'normal',
    choices: [
      {
        labelZh: '还是觉得这件事重要',
        labelEn: 'This still matters to me',
        effect: { mood: 15, connection: 1, focus: 5 },
        emotion: 'normal',
      },
      {
        labelZh: '哪有那么高尚，还是谈流量吧',
        labelEn: 'Let\'s be real, it\'s about the numbers',
        effect: { focus: 15 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 'day8_afternoon',
    day: 8,
    phase: 'afternoon',
    textZh: '直播间里有个叫"夜班小护士"的常驻观众，今天没来。\n\n你注意到了，但没说什么。',
    textEn: 'A regular viewer named "NightShiftNurse" wasn\'t there today.\n\nYou noticed. You didn\'t say anything.',
    laisaEmotion: 'sad',
    choices: [
      {
        labelZh: '去私信问问她还好吗',
        labelEn: 'Send her a message — is she okay?',
        effect: { connection: 2, mood: 10 },
        emotion: 'normal',
      },
      {
        labelZh: '观众来来去去，正常的',
        labelEn: 'Viewers come and go. Normal.',
        effect: { mood: -5 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 'day9_evening',
    day: 9,
    phase: 'evening',
    textZh: '你试了一个新游戏。出乎意料地难，当场卡关、骂出声——弹幕全都在笑。\n\n然后你也开始笑了。',
    textEn: 'You tried a new game. Unexpectedly hard. You got stuck and swore out loud — the chat all laughed.\n\nThen you started laughing too.',
    laisaEmotion: 'happy',
    choices: [
      {
        labelZh: '继续这个游戏，就玩卡关',
        labelEn: 'Keep playing this game, suffer together',
        effect: { mood: 20, followers: 50, focus: -5 },
        emotion: 'happy',
      },
      {
        labelZh: '还是换回熟悉的游戏',
        labelEn: 'Switch back to something familiar',
        effect: { mood: 10, focus: 10 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 'day10_evening',
    day: 10,
    phase: 'evening',
    textZh: '一条超级弹幕浮出来：\n\n"Laisa，你的直播陪我撑过了最难的那段时间。谢谢你。"\n\n你盯着那句话，忘记打游戏了。',
    textEn: 'A super chat floats up:\n\n"Laisa, your stream kept me going through the hardest time in my life. Thank you."\n\nYou stare at it and forget to play.',
    laisaEmotion: 'surprised',
    choices: [
      {
        labelZh: '认真回应，说说你自己的故事',
        labelEn: 'Respond honestly — share your own story',
        effect: { connection: 2, mood: 20, followers: 80 },
        emotion: 'happy',
      },
      {
        labelZh: '简单道谢，继续游戏',
        labelEn: 'Say thanks, keep going',
        effect: { mood: 10, followers: 30 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 'day11_morning',
    day: 11,
    phase: 'morning',
    textZh: '妈妈打来电话。\n\n你犹豫了三秒，接了。\n"最近吃饭了吗？" "……还好。"',
    textEn: 'Mom calls.\n\nYou hesitate three seconds, then pick up.\n"Are you eating?" "...yeah, I guess."',
    laisaEmotion: 'normal',
    choices: [
      {
        labelZh: '和她多聊一会儿',
        labelEn: 'Stay on the phone a little longer',
        effect: { mood: 18, connection: 1, energy: -5 },
        emotion: 'happy',
      },
      {
        labelZh: '说"忙"，挂了',
        labelEn: '"I\'m busy," and hang up',
        effect: { mood: -10, focus: 5 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 'day12_night',
    day: 12,
    phase: 'night',
    textZh: '你算了一下：上一次见到朋友，是三周前。\n\n不是因为吵架，也不是因为忙。只是……没想起来。',
    textEn: 'You count backwards: last time you saw a friend in person was three weeks ago.\n\nNot a fight. Not too busy. Just... you didn\'t think of it.',
    laisaEmotion: 'sad',
    choices: [
      {
        labelZh: '现在就发消息约周末见面',
        labelEn: 'Message them right now, plan for the weekend',
        effect: { connection: 2, mood: 15 },
        emotion: 'happy',
      },
      {
        labelZh: '算了，等这段忙完再说',
        labelEn: 'Wait until after this busy stretch',
        effect: { mood: -12, connection: -1 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 'day13_morning',
    day: 13,
    phase: 'morning',
    textZh: '最后一天。\n\n你打开窗帘，今天阳光很好。\n直播间里已经有人在等了。',
    textEn: 'Last day.\n\nYou open the curtains. Good sunlight today.\nSome people are already in the stream room waiting.',
    laisaEmotion: 'normal',
    choices: [
      {
        labelZh: '好。今天好好来。',
        labelEn: 'Alright. Let\'s make today count.',
        effect: { mood: 15, energy: 10, focus: 10 },
        emotion: 'happy',
      },
      {
        labelZh: '又是新的一天。',
        labelEn: 'Another day.',
        effect: { energy: 8, focus: 5 },
        emotion: 'normal',
      },
    ],
  },
];

// ── Stream Events ─────────────────────────────────────────────────────────────
// 4 randomly selected per stream session.
// Base follower values are intentionally large — volatility multiplies them.

export const STREAM_EVENTS: StreamEvent[] = [
  // ── Chat reactions ──────────────────────────────────────────────────────────
  {
    id: 's_died10',
    textZh: '弹幕：「Laisa 你这关已经死了十次了哈哈哈哈」',
    textEn: 'Chat: "Laisa you\'ve died 10 times on this section lmaooo"',
    choices: [
      {
        labelZh: '笑着说：我知道我知道',
        labelEn: 'Laugh it off: "I know I know"',
        effect: { followers: 120, mood: 10 },
        emotion: 'happy',
      },
      {
        labelZh: '不理，继续尝试',
        labelEn: 'Ignore it, keep trying',
        effect: { followers: 40, focus: 5 },
        emotion: 'normal',
      },
      {
        labelZh: '有点沮丧地说确实好难',
        labelEn: 'Say honestly: this is actually really hard',
        effect: { mood: -8, followers: 80 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 's_change_game',
    textZh: '弹幕刷屏：「换游戏换游戏换游戏」',
    textEn: 'Chat spams: "change game change game change game"',
    choices: [
      {
        labelZh: '好，听大家的，换一个',
        labelEn: 'Alright, let\'s switch',
        effect: { followers: 180, mood: 5 },
        emotion: 'happy',
      },
      {
        labelZh: '我就是要玩完这个',
        labelEn: 'I\'m finishing this one, that\'s final',
        effect: { followers: -80, focus: 15, mood: 10 },
        emotion: 'normal',
      },
      {
        labelZh: '投票决定？',
        labelEn: 'Let\'s put it to a vote?',
        effect: { followers: 140, mood: 8 },
        emotion: 'happy',
      },
    ],
  },
  {
    id: 's_state',
    textZh: '超级弹幕：「主播最近状态不太好吗，看起来有点累」',
    textEn: 'Super chat: "Streamer you seem a little tired lately, are you okay?"',
    choices: [
      {
        labelZh: '说说真实状态，没什么好藏的',
        labelEn: 'Talk about it honestly — nothing to hide',
        effect: { connection: 1, mood: 12, followers: 100 },
        emotion: 'normal',
      },
      {
        labelZh: '说没事哦，继续打游戏',
        labelEn: 'Say "I\'m fine!" and keep playing',
        effect: { followers: 40 },
        emotion: 'normal',
      },
      {
        labelZh: '强撑着说今天超级好',
        labelEn: 'Force a smile: "Today is amazing!"',
        effect: { mood: -12, followers: 20 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 's_new_viewer',
    textZh: '有人刚进来：「第一次看你的直播，你在玩什么？」',
    textEn: 'New viewer: "First time watching you, what are you playing?"',
    choices: [
      {
        labelZh: '认真介绍游戏和自己',
        labelEn: 'Introduce the game and yourself properly',
        effect: { followers: 160, mood: 10 },
        emotion: 'happy',
      },
      {
        labelZh: '简短说一句，继续玩',
        labelEn: 'Quick answer, keep playing',
        effect: { followers: 60 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_technical',
    textZh: '麦克风突然没有声音了……',
    textEn: 'The microphone suddenly cuts out...',
    choices: [
      {
        labelZh: '冷静修，打字跟大家说在修',
        labelEn: 'Fix it calmly, type in chat what\'s happening',
        effect: { followers: -40, mood: 5, focus: 10 },
        emotion: 'normal',
      },
      {
        labelZh: '慌了，说下播修好再来',
        labelEn: 'Panic — sign off to fix it',
        effect: { followers: -160, mood: -15 },
        emotion: 'sad',
      },
      {
        labelZh: '继续打游戏，用字幕代替声音',
        labelEn: 'Keep playing, use on-screen text',
        effect: { followers: 80, mood: 5 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_superchat',
    textZh: '有人发了条留言：「你的声音让人觉得不孤单」',
    textEn: 'Someone types: "Your voice makes people feel less alone"',
    choices: [
      {
        labelZh: '停下来认真回应这句话',
        labelEn: 'Stop and respond to this seriously',
        effect: { connection: 1, mood: 25, followers: 200 },
        emotion: 'happy',
      },
      {
        labelZh: '谢谢，继续玩',
        labelEn: 'Thank you, keep going',
        effect: { mood: 15, followers: 80 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_collab',
    textZh: '弹幕建议：「和别的主播开个联动呗」',
    textEn: 'Chat suggests: "You should collab with another streamer!"',
    choices: [
      {
        labelZh: '说在考虑，问大家想看谁',
        labelEn: 'Say you\'re thinking about it, ask who they want',
        effect: { followers: 140, mood: 10 },
        emotion: 'happy',
      },
      {
        labelZh: '不太想，我还是喜欢一个人',
        labelEn: 'Not really my thing, I prefer solo',
        effect: { followers: -60, focus: 8 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_challenge',
    textZh: '弹幕发起挑战：「死一次就给主播刷礼物！加油啊！」',
    textEn: 'Challenge from chat: "We\'ll send a gift every time you die! Let\'s go!"',
    choices: [
      {
        labelZh: '接受挑战，拼命玩',
        labelEn: 'Accept the challenge, go all out',
        effect: { followers: 220, mood: 20, energy: -10 },
        emotion: 'happy',
      },
      {
        labelZh: '笑着婉拒，专心通关',
        labelEn: 'Laugh and decline, focus on winning',
        effect: { followers: 80, focus: 15 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_silence',
    textZh: '直播间突然安静了，没什么弹幕……',
    textEn: 'The chat goes quiet. No messages for a while...',
    choices: [
      {
        labelZh: '主动找话题，"大家在吗？"',
        labelEn: 'Break the silence — "Is anyone there?"',
        effect: { followers: 100, mood: 5 },
        emotion: 'normal',
      },
      {
        labelZh: '专心打游戏就好',
        labelEn: 'Just focus on the game',
        effect: { focus: 15 },
        emotion: 'normal',
      },
      {
        labelZh: '有点不安，状态开始不稳',
        labelEn: 'Feel anxious, lose your footing',
        effect: { mood: -12, focus: -8 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 's_milestone',
    textZh: '你发现今天粉丝数到了一个整数——整整两千人。',
    textEn: 'You notice the follower count just hit a round number — exactly two thousand.',
    choices: [
      {
        labelZh: '截图纪念，感谢大家陪着你',
        labelEn: 'Screenshot it, thank everyone for being here',
        effect: { mood: 25, followers: 160, connection: 1 },
        emotion: 'happy',
      },
      {
        labelZh: '数字而已，继续',
        labelEn: 'Just a number, keep going',
        effect: { focus: 10 },
        emotion: 'normal',
      },
    ],
  },

  // ── Drama & pressure ────────────────────────────────────────────────────────
  {
    id: 's_hate_raid',
    textZh: '突然涌进来一群陌生账号，开始刷仇恨弹幕……',
    textEn: 'A wave of unknown accounts floods in, spamming hate comments...',
    choices: [
      {
        labelZh: '开启慢速模式，冷静说一声不欢迎骚扰',
        labelEn: 'Enable slow mode, calmly say harassment isn\'t welcome',
        effect: { followers: -100, mood: -8, focus: 10 },
        emotion: 'normal',
      },
      {
        labelZh: '直接暂停直播，等风头过去',
        labelEn: 'Pause the stream and wait it out',
        effect: { followers: -240, mood: -20 },
        emotion: 'sad',
      },
      {
        labelZh: '无视他们，真粉丝自然会留',
        labelEn: 'Ignore them — real fans will stay',
        effect: { followers: -60, focus: 12, connection: 1 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_algorithm',
    textZh: '后台数据突然涨了——平台把你推上了推荐位！',
    textEn: 'Your backend stats spike — the platform just pushed you to the recommendation feed!',
    choices: [
      {
        labelZh: '马上拉高质量，抓住这波流量',
        labelEn: 'Raise the quality now — capitalize on this wave',
        effect: { followers: 300, energy: -15, focus: -8 },
        emotion: 'happy',
      },
      {
        labelZh: '正常发挥就好，别紧张',
        labelEn: 'Just play normally, don\'t overthink it',
        effect: { followers: 180, mood: 8 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_fanart',
    textZh: '有人在直播间贴了一张给你画的同人图……画得真的很好。',
    textEn: 'Someone posts fan art they drew of you in chat... it\'s actually really good.',
    choices: [
      {
        labelZh: '大声表扬，让大家看看',
        labelEn: 'Shout them out, show the whole chat',
        effect: { followers: 200, mood: 20, connection: 1 },
        emotion: 'happy',
      },
      {
        labelZh: '私信感谢，继续游戏',
        labelEn: 'DM a thank-you and keep playing',
        effect: { mood: 15, followers: 80 },
        emotion: 'happy',
      },
    ],
  },
  {
    id: 's_big_donation',
    textZh: '一笔超大额打赏进来，弹幕瞬间炸了……',
    textEn: 'A massive donation comes in. Chat instantly explodes...',
    choices: [
      {
        labelZh: '真诚感谢，分享一点自己的故事',
        labelEn: 'Thank them genuinely, share a little about yourself',
        effect: { followers: 350, mood: 25, connection: 2 },
        emotion: 'surprised',
      },
      {
        labelZh: '激动过头，说话开始语无伦次',
        labelEn: 'Get too excited and start rambling',
        effect: { followers: 180, mood: 10, focus: -10 },
        emotion: 'happy',
      },
    ],
  },
  {
    id: 's_lag',
    textZh: '直播卡了。弹幕开始刷：「卡卡卡卡」「主播你掉帧了」……',
    textEn: 'The stream is lagging. Chat fills up with "lag lag lag" and "your frames are dropping"...',
    choices: [
      {
        labelZh: '立刻降低码率，解释情况',
        labelEn: 'Drop bitrate immediately and explain what\'s happening',
        effect: { followers: -60, mood: 5 },
        emotion: 'normal',
      },
      {
        labelZh: '坚持继续，假装没事',
        labelEn: 'Push through, pretend nothing\'s wrong',
        effect: { followers: -180, mood: -10, focus: -5 },
        emotion: 'sad',
      },
      {
        labelZh: '调侃卡顿，和弹幕一起笑',
        labelEn: 'Make a joke about it, laugh along with chat',
        effect: { followers: 80, mood: 12 },
        emotion: 'happy',
      },
    ],
  },
  {
    id: 's_trending',
    textZh: '有人说你的名字上了今日热榜！不知道是什么原因……',
    textEn: 'Someone says your name is on today\'s trending list! Not sure why...',
    choices: [
      {
        labelZh: '立刻蹭一波热度，提一下',
        labelEn: 'Ride the wave — mention it on stream',
        effect: { followers: 400, mood: 10, focus: -5 },
        emotion: 'surprised',
      },
      {
        labelZh: '等搞清楚再说，先继续直播',
        labelEn: 'Wait until you know why, keep streaming',
        effect: { followers: 160, focus: 8 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_sniping',
    textZh: '一个粉丝数是你十倍的主播在直播间出现，弹幕瞬间乱了……',
    textEn: 'A streamer with 10x your followers just entered your chat. Things get chaotic...',
    choices: [
      {
        labelZh: '礼貌问候，顺势互动',
        labelEn: 'Greet them warmly, interact naturally',
        effect: { followers: 280, mood: 8, connection: 1 },
        emotion: 'surprised',
      },
      {
        labelZh: '不理，专注自己的内容',
        labelEn: 'Ignore them, stay focused on your content',
        effect: { followers: 60, focus: 15 },
        emotion: 'normal',
      },
      {
        labelZh: '紧张起来，发挥失常',
        labelEn: 'Get nervous and lose your groove',
        effect: { followers: -80, mood: -15, focus: -10 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 's_clip_viral',
    textZh: '有人把你五分钟前的精彩片段剪出来，短短几分钟播放量破万了……',
    textEn: 'Someone clipped your highlight from five minutes ago. It hit 10,000 views in minutes...',
    choices: [
      {
        labelZh: '转发并感谢，趁热打铁',
        labelEn: 'Repost and thank them, strike while it\'s hot',
        effect: { followers: 500, mood: 20 },
        emotion: 'happy',
      },
      {
        labelZh: '继续直播，这种事随它去',
        labelEn: 'Keep streaming, let it play out',
        effect: { followers: 240, focus: 5 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_hate_comment',
    textZh: '一条刻薄的弹幕出现：「就这水平也配叫主播？」',
    textEn: 'A harsh comment appears: "You call yourself a streamer with this skill level?"',
    choices: [
      {
        labelZh: '正面回应，说说自己为什么在做这件事',
        labelEn: 'Address it directly — explain why you do this',
        effect: { followers: 160, mood: -5, connection: 1 },
        emotion: 'normal',
      },
      {
        labelZh: '封禁，继续正常直播',
        labelEn: 'Ban them, move on normally',
        effect: { followers: 80, mood: 5 },
        emotion: 'normal',
      },
      {
        labelZh: '被刺到了，心情直线下降',
        labelEn: 'It stings. Your mood crashes.',
        effect: { followers: -40, mood: -25 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 's_spoiler',
    textZh: '有人在弹幕里剧透了游戏最终BOSS——你还没打到那里。',
    textEn: 'Someone just spoiled the final boss in chat — you\'re nowhere near there yet.',
    choices: [
      {
        labelZh: '幽默带过，"感谢剧透，以后先开字幕"',
        labelEn: 'Joke it off: "Thanks for the spoiler, turning on subtitles now"',
        effect: { followers: 120, mood: 8 },
        emotion: 'happy',
      },
      {
        labelZh: '认真请大家不要剧透',
        labelEn: 'Seriously ask everyone to stop spoiling',
        effect: { followers: 40, focus: 10 },
        emotion: 'normal',
      },
      {
        labelZh: '沉默，但心里有点不高兴',
        labelEn: 'Go quiet. You\'re a little annoyed.',
        effect: { mood: -15, focus: -8 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 's_argue',
    textZh: '两个粉丝在弹幕里吵起来了，场面越来越难看……',
    textEn: 'Two viewers start arguing in chat. It\'s getting ugly...',
    choices: [
      {
        labelZh: '开启慢速模式，温柔劝架',
        labelEn: 'Enable slow mode and calmly mediate',
        effect: { followers: 60, mood: 5, connection: 1 },
        emotion: 'normal',
      },
      {
        labelZh: '用幽默化解，讲个段子转移注意',
        labelEn: 'Defuse with humor, tell a joke to change the subject',
        effect: { followers: 140, mood: 10 },
        emotion: 'happy',
      },
      {
        labelZh: '直接禁言双方，我不管这些',
        labelEn: 'Mute both of them — not my problem',
        effect: { followers: -80, mood: -8 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 's_request_face',
    textZh: '弹幕突然开始刷：「开摄像头！开摄像头！」',
    textEn: 'Chat starts spamming: "Show your face! Face cam! Face cam!"',
    choices: [
      {
        labelZh: '开了，大家反应热烈',
        labelEn: 'Turn it on — chat goes wild',
        effect: { followers: 320, mood: 15 },
        emotion: 'happy',
      },
      {
        labelZh: '解释一下不开摄像头的原因',
        labelEn: 'Explain why you prefer no face cam',
        effect: { followers: 80, connection: 1 },
        emotion: 'normal',
      },
      {
        labelZh: '直接拒绝，心里有点堵',
        labelEn: 'Flat no. It leaves you feeling off.',
        effect: { followers: -60, mood: -10 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 's_personal_best',
    textZh: '你刚刚打出了这个游戏的个人最高分——弹幕全体起立。',
    textEn: 'You just hit your personal best score. The entire chat stands up.',
    choices: [
      {
        labelZh: '庆祝！截图发出去！',
        labelEn: 'Celebrate! Screenshot it and post it!',
        effect: { followers: 260, mood: 22, focus: 5 },
        emotion: 'happy',
      },
      {
        labelZh: '淡定，说还有进步空间',
        labelEn: 'Stay calm — say there\'s still room to improve',
        effect: { followers: 120, focus: 12 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_platform_down',
    textZh: '平台推送一条警告：今晚可能有服务器维护，直播可能随时中断。',
    textEn: 'Platform sends a warning: server maintenance tonight — stream may cut out at any time.',
    choices: [
      {
        labelZh: '提前告知观众，做好心理准备',
        labelEn: 'Tell viewers upfront, mentally prepare together',
        effect: { followers: 80, mood: 5, connection: 1 },
        emotion: 'normal',
      },
      {
        labelZh: '赌一把，不说，继续播',
        labelEn: 'Gamble on it — don\'t mention it, keep going',
        effect: { followers: 180, mood: -5, focus: -8 },
        emotion: 'normal',
      },
    ],
  },
  {
    id: 's_viewer_crisis',
    textZh: '一个常驻观众突然发消息说他今晚很难过，想找人说说话。',
    textEn: 'A regular viewer messages privately — they\'re having a really hard night and need to talk.',
    choices: [
      {
        labelZh: '暂停游戏，好好听他说',
        labelEn: 'Pause the game and really listen',
        effect: { followers: 140, mood: 15, connection: 2, energy: -8 },
        emotion: 'normal',
      },
      {
        labelZh: '发个安慰，说直播结束后再聊',
        labelEn: 'Send comfort, say you\'ll talk after stream',
        effect: { followers: 60, mood: 5, connection: 1 },
        emotion: 'normal',
      },
      {
        labelZh: '不知道怎么处理，沉默了',
        labelEn: 'Freeze. You don\'t know what to say.',
        effect: { mood: -15, followers: -40 },
        emotion: 'sad',
      },
    ],
  },
  {
    id: 's_comparison',
    textZh: '弹幕里有人说：「你和××主播差远了，人家这会儿有五万在线」',
    textEn: 'Someone in chat says: "You\'re nothing like [big streamer], they have 50k viewers right now"',
    choices: [
      {
        labelZh: '笑笑：我们走不同的路，没关系',
        labelEn: 'Smile: "We\'re on different paths, and that\'s fine"',
        effect: { followers: 100, mood: 8, connection: 1 },
        emotion: 'normal',
      },
      {
        labelZh: '不作声，暗自较劲',
        labelEn: 'Stay quiet. Quietly determined.',
        effect: { focus: 18, mood: -8 },
        emotion: 'normal',
      },
      {
        labelZh: '心里塌了一下，失去了状态',
        labelEn: 'Something drops inside you. You lose your rhythm.',
        effect: { followers: -120, mood: -20, focus: -12 },
        emotion: 'sad',
      },
    ],
  },
];

export function pickStreamEvents(count = 4): StreamEvent[] {
  const shuffled = [...STREAM_EVENTS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}
