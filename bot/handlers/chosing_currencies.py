from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from fluent.runtime import FluentLocalization

from bot.keyboards.build_row_keyboard import build_row_keyboard
from bot.config import settings
from .currency_converter import CurrencyConverter




class ChoseCurrencyCode(StatesGroup):
    """
    Состояния для процесса выбора валют

    Attributes:
        choosing_currency_from (State): Состояние выбора валюты, из которой конвертировать
        choosing_currency_to (State): Состояние выбора валюты, в которую конвертировать
    """
    choosing_currency_from = State()
    choosing_currency_to = State()


router = Router()
chosen_currency_by_user = CurrencyConverter.user_data

@router.message(StateFilter(None), Command("currencies"))
async def command_chose_currency(message: Message, l10n: FluentLocalization, state: FSMContext):
    """
    Хэндлер на команду выбора валюты

    :param message: сообщение от пользователя
    :param l10n: объект локализации
    :param state: состояние FSM
    """
    await message.answer(
        l10n.format_value("chose_currency_code_from"),
        reply_markup=build_row_keyboard(settings.top_20_fiat)
    )
    await state.set_state(ChoseCurrencyCode.choosing_currency_from)

@router.message(
    StateFilter(ChoseCurrencyCode.choosing_currency_from),
    F.text.lower().in_(settings.supported_currency)
)
async def currency_from_chosen(message: Message, l10n: FluentLocalization, state: FSMContext):
    """
    Хэндлер на выбор валюты, из которой конвертировать

    :param message: сообщение от пользователя
    :param l10n: объект локализации
    :param state: состояние FSM
    """
    await state.update_data(chosen_currency=message.text.lower())
    await message.answer(text=l10n.format_value("chose_currency_code_to"),
                         reply_markup=build_row_keyboard(settings.top_20_fiat))
    chosen_currency_by_user["chosen_currency_code_from"] = message.text.lower()
    await state.set_state(ChoseCurrencyCode.choosing_currency_to)

@router.message(StateFilter("ChoseCurrencyCode:choosing_currency_from"))
async def currency_from_chosen_incorrectly(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на некорректный выбор валюты, из которой конвертировать

    :param message: сообщение от пользователя
    :param l10n: объект локализации
    """
    await message.answer(
        l10n.format_value("incorrectly_chosen_currency"),
        reply_markup=build_row_keyboard(settings.top_20_fiat)
    )

@router.message(
    StateFilter(ChoseCurrencyCode.choosing_currency_to),
    F.text.lower().in_(settings.supported_currency)
)
async def currency_to_chosen(message: Message, l10n: FluentLocalization, state: FSMContext):
    """
    Хэндлер на выбор валюты, в которую конвертировать

    :param message: сообщение от пользователя
    :param l10n: объект локализации
    :param state: состояние FSM
    """
    # chosen_currency_by_user = await state.get_data()
    await message.answer(text=l10n.format_value("chosen_currency_code_from_to", {
        "chosen_currency_code_from": chosen_currency_by_user['chosen_currency_code_from'].upper(),
        "chosen_currency_code_to": message.text.upper()}), 
                         reply_markup=ReplyKeyboardRemove())
    chosen_currency_by_user["chosen_currency_code_to"] = message.text.lower()
    await state.clear()

@router.message(StateFilter("ChoseCurrencyCode:choosing_currency_to"))
async def currency_to_chosen_incorrectly(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на некорректный выбор валюты, в которую конвертировать

    :param message: сообщение от пользователя
    :param l10n: объект локализации
    """
    await message.answer(
        l10n.format_value("incorrectly_chosen_currency"),
        reply_markup=build_row_keyboard(settings.top_20_fiat)
    )

@router.message(F.text)
async def text_message(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на текстовые сообщения от пользователя

    :param message: сообщение от пользователя дла отправки валюты
    :param l10n: объект локализации
    """
    if answer := await CurrencyConverter(l10n).build_answer(message):
        await message.answer(answer, parse_mode="HTML")
   