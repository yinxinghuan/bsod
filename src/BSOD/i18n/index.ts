const translations = {
  zh: {
    title: '蓝屏',
    subtitle: '一个人的直播间',
    startBtn: '开机',
    day: '第 {n} 天',
    of13: '/ 13',
    phase_morning: '早晨',
    phase_afternoon: '下午',
    phase_evening: '晚上',
    phase_night: '深夜',
    stat_energy: '体力',
    stat_mood: '心情',
    stat_focus: '专注',
    stat_followers: '粉丝',
    hidden_connection: '（羁绊）',
    chooseAction: '选择接下来做什么',
    dayEndTitle: '今天结束了',
    dayEndContinue: '继续',
    streamTitle: '正在直播中',
    streamEnd: '结束直播',
    streamGained: '+{n} 粉丝',
    continueBtn: '继续',
    replayBtn: '重新开始',
    deathTitle_energy: '体力耗尽',
    deathTitle_mood: '心情崩溃',
    deathTitle_followers: '被平台清退',
    deathTitle_focus: '焦虑崩溃',
    deathDesc_energy: '你趴在键盘上，显示器还亮着。直播间里没人知道。',
    deathDesc_mood: '你关掉摄像头，然后就再也没有打开过。',
    deathDesc_followers: '粉丝流失了。平台给了你一封通知邮件，你没有打开。',
    deathDesc_focus: '脑子里像是一片空白。你坐在电脑前，却不知道要干什么。开播按钮就在那里，你没有点。',
    'ending.online.title': '在线',
    'ending.online.sub': '你还在。他们也还在。',
    'ending.online.text': '你在一个不可能赢的游戏里赢了。不只是数字——有些人知道你叫 Laisa，不只是某个主播。',
    'ending.offline.title': '离线',
    'ending.offline.sub': '屏幕一关，就什么都没了。',
    'ending.offline.text': '数字往上走了。你忘了在什么时候停止回复消息。直播间里总是满的，但你开始感到，总有什么东西不在了。',
    'ending.restart.title': '重启',
    'ending.restart.sub': '没有爆款。但有人在等。',
    'ending.restart.text': '没有那种一夜爆红的高光，粉丝数长得慢。但他们每次开播都在，你也知道他们叫什么名字。也许这已经够了。',
    'ending.bsod.title': 'BSOD',
    'ending.bsod.sub': '系统崩溃',
    'ending.bsod.text': 'A fatal error has occurred. Your existence could not be saved.',
    errorCode: '错误代码：0x0000LAISA',
    errorCodeEn: 'SYSTEM_THREAD_EXCEPTION_NOT_HANDLED',
    goodMorning: '早上好。',
    followersUnit: '人',
  },
  en: {
    title: 'BSOD',
    subtitle: 'A Solo Streaming Life',
    startBtn: 'Boot Up',
    day: 'Day {n}',
    of13: '/ 13',
    phase_morning: 'Morning',
    phase_afternoon: 'Afternoon',
    phase_evening: 'Evening',
    phase_night: 'Late Night',
    stat_energy: 'Energy',
    stat_mood: 'Mood',
    stat_focus: 'Focus',
    stat_followers: 'Followers',
    hidden_connection: '(bond)',
    chooseAction: 'What will you do?',
    dayEndTitle: 'Day Done',
    dayEndContinue: 'Continue',
    streamTitle: 'Live Streaming',
    streamEnd: 'End Stream',
    streamGained: '+{n} followers',
    continueBtn: 'Continue',
    replayBtn: 'Restart',
    deathTitle_energy: 'Exhausted',
    deathTitle_mood: 'Burned Out',
    deathTitle_followers: 'Platform Dropped You',
    deathTitle_focus: 'Burned Out',
    deathDesc_energy: 'You passed out at the keyboard. The monitor was still on. Nobody in the stream noticed.',
    deathDesc_mood: 'You turned off the camera. And never turned it back on.',
    deathDesc_followers: 'The followers left. The platform sent an email. You didn\'t open it.',
    deathDesc_focus: 'Your mind went blank. You sat in front of the computer not knowing what to do. The go-live button was right there. You didn\'t press it.',
    'ending.online.title': 'Online',
    'ending.online.sub': 'You\'re still here. And so are they.',
    'ending.online.text': 'You won in a game that wasn\'t supposed to be winnable. Not just the numbers — some people know your name is Laisa, not just "some streamer".',
    'ending.offline.title': 'Offline',
    'ending.offline.sub': 'When the screen goes dark, there\'s nothing.',
    'ending.offline.text': 'The numbers went up. You forgot when you stopped answering messages. The stream was always full. But something felt missing.',
    'ending.restart.title': 'Restart',
    'ending.restart.sub': 'No viral moment. But people showed up.',
    'ending.restart.text': 'No overnight explosion, slow follower growth. But they were there every time you went live, and you knew their usernames. Maybe that\'s enough.',
    'ending.bsod.title': 'BSOD',
    'ending.bsod.sub': 'Critical System Failure',
    'ending.bsod.text': 'A fatal error has occurred. Your existence could not be saved.',
    errorCode: 'Error: 0x0000LAISA',
    errorCodeEn: 'SYSTEM_THREAD_EXCEPTION_NOT_HANDLED',
    goodMorning: 'Good morning.',
    followersUnit: '',
  },
} as const;

type Locale = keyof typeof translations;

function detectLocale(): Locale {
  const override = typeof localStorage !== 'undefined' ? localStorage.getItem('bsod_locale') : null;
  if (override === 'en' || override === 'zh') return override;
  const lang = (typeof navigator !== 'undefined' ? navigator.language : 'en').toLowerCase();
  return lang.startsWith('zh') ? 'zh' : 'en';
}

const locale = detectLocale();

export function t(key: string, vars?: { n?: number | string }): string {
  const dict = translations[locale] as Record<string, string>;
  let str = dict[key] ?? (translations.en as Record<string, string>)[key] ?? key;
  if (vars?.n !== undefined) str = str.replace('{n}', String(vars.n));
  return str;
}

export function getText(zh: string, en: string): string {
  return locale === 'zh' ? zh : en;
}

export function useLocale() {
  return { t, locale, getText };
}
