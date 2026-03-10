addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const TOKEN = '8687686811:AAFodDPyMBlYGBChIimWkZvrvnf6YEJYx38'

async function handleRequest(request) {
  if (request.method === 'POST') {
    const body = await request.json()
    
    // Проверяем что пришло сообщение
    const chatId = body.message?.chat?.id
    const text = body.message?.text

    if (!chatId) return new Response('No chat_id', {status: 400})

    // Список ссылок на карты
    const cards = [
      'https://github.com/AnastasiyaRemeslova/vdoh_vydoh_cards_bot/blob/e5ae782813b7b62b406fbca924c8bb86af757fd1/cards/%D0%92%D0%B4%D0%BE%D1%85-%D0%92%D1%8B%D0%B4%D0%BE%D1%85.%20%D0%91%D0%BB%D0%BE%D0%BA%201.01.png',
      'https://github.com/AnastasiyaRemeslova/vdoh_vydoh_cards_bot/blob/e5ae782813b7b62b406fbca924c8bb86af757fd1/cards/%D0%92%D0%B4%D0%BE%D1%85-%D0%92%D1%8B%D0%B4%D0%BE%D1%85.%20%D0%91%D0%BB%D0%BE%D0%BA%201.02.png',
      'https://github.com/AnastasiyaRemeslova/vdoh_vydoh_cards_bot/blob/e5ae782813b7b62b406fbca924c8bb86af757fd1/cards/%D0%92%D0%B4%D0%BE%D1%85-%D0%92%D1%8B%D0%B4%D0%BE%D1%85.%20%D0%91%D0%BB%D0%BE%D0%BA%201.03.png'
    ]

    if (text === '/start') {
      // Кнопка inline
      const keyboard = {
        inline_keyboard: [
          [{text: "Получить карточку", callback_data: "card"}]
        ]
      }
      await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          chat_id: chatId,
          text: "Нажмите кнопку, чтобы получить карточку",
          reply_markup: keyboard
        })
      })
    }

    // Callback от кнопки
    const callbackData = body.callback_query?.data
    if (callbackData === 'card') {
      const callbackChatId = body.callback_query.message.chat.id
      const card = cards[Math.floor(Math.random() * cards.length)]

      await fetch(`https://api.telegram.org/bot${TOKEN}/sendPhoto`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          chat_id: callbackChatId,
          photo: card,
          caption: "Вот ваша карточка!"
        })
      })

      // Ответ на callback_query (чтобы кнопка перестала крутиться)
      const callbackId = body.callback_query.id
      await fetch(`https://api.telegram.org/bot${TOKEN}/answerCallbackQuery`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ callback_query_id: callbackId })
      })
    }

    return new Response('ok')
  }

  return new Response('Method not allowed', { status: 405 })
}