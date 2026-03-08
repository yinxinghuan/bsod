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
// 3 randomly selected per stream session.

export const STREAM_EVENTS: StreamEvent[] = [
  {
    id: 's_died10',
    textZh: '弹幕：「Laisa 你这关已经死了十次了哈哈哈哈」',
    textEn: 'Chat: "Laisa you\'ve died 10 times on this section lmaooo"',
    choices: [
      {
        labelZh: '笑着说：我知道我知道',
        labelEn: 'Laugh it off: "I know I know"',
        effect: { followers: 30, mood: 10 },
        emotion: 'happy',
      },
      {
        labelZh: '不理，继续尝试',
        labelEn: 'Ignore it, keep trying',
        effect: { followers: 10, focus: 5 },
        emotion: 'normal',
      },
      {
        labelZh: '有点沮丧地说确实好难',
        labelEn: 'Say honestly: this is actually really hard',
        effect: { mood: -8, followers: 20 },
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
        effect: { followers: 45, mood: 5 },
        emotion: 'happy',
      },
      {
        labelZh: '我就是要玩完这个',
        labelEn: 'I\'m finishing this one, that\'s final',
        effect: { followers: -20, focus: 15, mood: 10 },
        emotion: 'normal',
      },
      {
        labelZh: '投票决定？',
        labelEn: 'Let\'s put it to a vote?',
        effect: { followers: 35, mood: 8 },
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
        effect: { connection: 1, mood: 12, followers: 25 },
        emotion: 'normal',
      },
      {
        labelZh: '说没事哦，继续打游戏',
        labelEn: 'Say "I\'m fine!" and keep playing',
        effect: { followers: 10 },
        emotion: 'normal',
      },
      {
        labelZh: '强撑着说今天超级好',
        labelEn: 'Force a smile: "Today is amazing!"',
        effect: { mood: -12, followers: 5 },
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
        effect: { followers: 40, mood: 10 },
        emotion: 'happy',
      },
      {
        labelZh: '简短说一句，继续玩',
        labelEn: 'Quick answer, keep playing',
        effect: { followers: 15 },
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
        effect: { followers: -10, mood: 5, focus: 10 },
        emotion: 'normal',
      },
      {
        labelZh: '慌了，说下播修好再来',
        labelEn: 'Panic — sign off to fix it',
        effect: { followers: -40, mood: -15 },
        emotion: 'sad',
      },
      {
        labelZh: '继续打游戏，用字幕代替声音',
        labelEn: 'Keep playing, use on-screen text',
        effect: { followers: 20, mood: 5 },
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
        effect: { connection: 1, mood: 25, followers: 50 },
        emotion: 'happy',
      },
      {
        labelZh: '谢谢，继续玩',
        labelEn: 'Thank you, keep going',
        effect: { mood: 15, followers: 20 },
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
        effect: { followers: 35, mood: 10 },
        emotion: 'happy',
      },
      {
        labelZh: '不太想，我还是喜欢一个人',
        labelEn: 'Not really my thing, I prefer solo',
        effect: { followers: -15, focus: 8 },
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
        effect: { followers: 55, mood: 20, energy: -10 },
        emotion: 'happy',
      },
      {
        labelZh: '笑着婉拒，专心通关',
        labelEn: 'Laugh and decline, focus on winning',
        effect: { followers: 20, focus: 15 },
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
        effect: { followers: 25, mood: 5 },
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
        effect: { mood: 25, followers: 40, connection: 1 },
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
];

export function pickStreamEvents(count = 3): StreamEvent[] {
  const shuffled = [...STREAM_EVENTS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}
