from aiogram.utils import markdown as fmt


def choosen_form(drug):
    msg = fmt.text(
        fmt.text('Название:', drug['nmprep']),
        fmt.text('Торговая марка:', drug['nmmnn']),
        fmt.text('Форма выпуска:', drug['form']),
        sep='\n',
    )
    return msg

def finded_pharmacy(pharmacy):
    msg = fmt.text(
        fmt.text('Название:', pharmacy['nmfirm']),
        fmt.text('Адрес:', pharmacy['str']),
        fmt.text('Время работы:', pharmacy['time']),
        fmt.bold('Цена:', pharmacy['price']),
        sep='\n'
    )
    return msg

def waiting(choosen_form):
    msg = fmt.text(
        fmt.text('Запомнил.'),
        fmt.text('Название:', choosen_form['nmprep']),
        fmt.text('Торговая марка:', choosen_form['nmmnn']),
        fmt.text('Форма:', choosen_form['form']),
        fmt.text('Можешь отправить еще или начать поиск'),
        fmt.text('Для отмены есть /cancel'),
        sep='\n'
    )
    return msg