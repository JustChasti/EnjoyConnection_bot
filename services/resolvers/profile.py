"""Заполнение и редактирование профиля (пол, возраст, цель общения)"""

from aiogram.types import (
    Message,
    CallbackQuery
)
from aiogram.fsm.context import FSMContext

from config import texts
from services.api_requests import api_client
from services.decorators import handle_resolver_errors
from services.states import StateMachine
from services.resolvers.keyboards import (
    get_menu_keyboard,
    get_survey_gender_keyboard,
    get_survey_goal_keyboard,
    get_survey_mask_keyboard,
    get_profile_edit_keyboard,
    get_edit_gender_keyboard,
    get_edit_goal_keyboard,
    get_edit_back_keyboard,
    get_mask_select_keyboard,
    get_mask_confirm_keyboard,
)
from services.resolvers.user_chat import render_lk


def _profile_error_text(response: dict) -> str:
    """Маппит код ошибки правки профиля на текст для пользователя"""
    code = response.get("error", "")
    return texts.PROFILE_ERROR_MESSAGES.get(code, texts.PROFILE_UNKNOWN_ERROR)


async def _try_set_age(user_id: int, raw: str):
    """Парсит и отправляет возраст на сервер.

    Возвращает (status, response): status = 'ok' | 'not_number' | 'error'.
    """
    try:
        age = int(raw.strip())
    except (ValueError, AttributeError, TypeError):
        return "not_number", None
    response = await api_client.update_personality(user_id, age=age)
    if response.get("success"):
        return "ok", None
    return "error", response


# === ПОШАГОВАЯ АНКЕТА (кнопка «Заполнить») === #

@handle_resolver_errors
async def resolve_profile_fill(callback: CallbackQuery):
    """Старт анкеты — спрашиваем пол"""
    await callback.answer()
    await callback.message.answer(
        texts.PROFILE_ASK_GENDER, reply_markup=get_survey_gender_keyboard()
    )


@handle_resolver_errors
async def resolve_profile_skip(callback: CallbackQuery, state: FSMContext):
    """Пропуск анкеты"""
    await callback.answer()
    await state.clear()
    await callback.message.answer(texts.PROFILE_SKIPPED, reply_markup=get_menu_keyboard())


@handle_resolver_errors
async def resolve_survey_gender(callback: CallbackQuery, state: FSMContext):
    """Пол выбран — сохраняем и спрашиваем возраст"""
    await callback.answer()
    gender = callback.data.removeprefix("survey_gender_")
    response = await api_client.update_personality(callback.from_user.id, gender=gender)
    if not response.get("success"):
        await callback.message.answer(_profile_error_text(response))
        return
    await state.set_state(StateMachine.profile_survey_age)
    await callback.message.answer(texts.PROFILE_ASK_AGE)


@handle_resolver_errors
async def resolve_survey_age(message: Message, state: FSMContext):
    """Возраст введён — сохраняем и спрашиваем цель общения"""
    status, response = await _try_set_age(message.from_user.id, message.text)
    if status == "not_number":
        await message.answer(texts.PROFILE_AGE_NOT_NUMBER)
        return
    if status == "error":
        if response.get("error") == "invalid_value":
            # некорректный возраст — остаёмся в состоянии для повторного ввода
            await message.answer(texts.PROFILE_ERROR_MESSAGES["invalid_value"])
            return
        # терминальная ошибка — выходим из состояния, чтобы не запереть пользователя
        await state.clear()
        await message.answer(_profile_error_text(response), reply_markup=get_menu_keyboard())
        return
    await state.set_state(None)
    await message.answer(texts.PROFILE_ASK_GOAL, reply_markup=get_survey_goal_keyboard())


@handle_resolver_errors
async def resolve_survey_goal(callback: CallbackQuery, state: FSMContext):
    """Цель общения выбрана — переходим к выбору персонажа"""
    await callback.answer()
    goal = callback.data.removeprefix("survey_goal_")
    response = await api_client.update_relationship_goal(callback.from_user.id, goal)
    if not response.get("success"):
        await callback.message.answer(_profile_error_text(response))
        return
    await callback.message.answer(
        texts.MASK_SELECT_MENU, reply_markup=get_survey_mask_keyboard()
    )


@handle_resolver_errors
async def resolve_survey_mask(callback: CallbackQuery, state: FSMContext):
    """Персонаж выбран в анкете — завершаем анкету (без предупреждения)"""
    await callback.answer()
    mask_name = callback.data.removeprefix("mask_goal_")
    response = await api_client.update_mask(callback.from_user.id, mask_name)
    if not response.get("success"):
        await callback.message.answer(_profile_error_text(response))
        return
    await state.clear()
    await callback.message.answer(texts.PROFILE_SURVEY_DONE, reply_markup=get_menu_keyboard())


# === РЕДАКТИРОВАНИЕ ПРОФИЛЯ (из личного кабинета) === #

@handle_resolver_errors
async def resolve_profile_edit_menu(callback: CallbackQuery, state: FSMContext):
    """Показ меню редактирования профиля (также обработчик кнопки «Назад»)"""
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        texts.PROFILE_EDIT_MENU, reply_markup=get_profile_edit_keyboard()
    )


@handle_resolver_errors
async def resolve_edit_to_lk(callback: CallbackQuery, state: FSMContext):
    """Назад в личный кабинет"""
    await callback.answer()
    await state.clear()
    await render_lk(callback.message, callback.from_user.id)


@handle_resolver_errors
async def resolve_edit_age_request(callback: CallbackQuery, state: FSMContext):
    """Запрос ввода возраста"""
    await callback.answer()
    await state.set_state(StateMachine.profile_edit_age)
    await callback.message.answer(texts.PROFILE_ASK_AGE, reply_markup=get_edit_back_keyboard())


@handle_resolver_errors
async def resolve_edit_age(message: Message, state: FSMContext):
    """Сохранение введённого возраста"""
    status, response = await _try_set_age(message.from_user.id, message.text)
    if status == "not_number":
        await message.answer(texts.PROFILE_AGE_NOT_NUMBER)
        return
    if status == "error":
        if response.get("error") == "invalid_value":
            await message.answer(texts.PROFILE_ERROR_MESSAGES["invalid_value"])
            return
        # терминальная ошибка (например, нужна подписка) — выходим из состояния
        await state.clear()
        await message.answer(
            _profile_error_text(response), reply_markup=get_profile_edit_keyboard()
        )
        return
    await state.clear()
    await message.answer(
        texts.PROFILE_AGE_UPDATED, reply_markup=get_profile_edit_keyboard()
    )


@handle_resolver_errors
async def resolve_edit_gender_request(callback: CallbackQuery):
    """Показ кнопок выбора пола"""
    await callback.answer()
    await callback.message.answer(
        texts.PROFILE_ASK_GENDER, reply_markup=get_edit_gender_keyboard()
    )


@handle_resolver_errors
async def resolve_edit_gender_set(callback: CallbackQuery):
    """Сохранение выбранного пола"""
    await callback.answer()
    gender = callback.data.removeprefix("pedit_gender_")
    response = await api_client.update_personality(callback.from_user.id, gender=gender)
    if not response.get("success"):
        await callback.message.answer(_profile_error_text(response))
        return
    await callback.message.answer(
        texts.PROFILE_GENDER_UPDATED, reply_markup=get_profile_edit_keyboard()
    )


@handle_resolver_errors
async def resolve_edit_goal_request(callback: CallbackQuery):
    """Показ кнопок выбора цели общения"""
    await callback.answer()
    await callback.message.answer(
        texts.PROFILE_ASK_GOAL, reply_markup=get_edit_goal_keyboard()
    )


@handle_resolver_errors
async def resolve_edit_goal_set(callback: CallbackQuery):
    """Сохранение выбранной цели общения"""
    await callback.answer()
    goal = callback.data.removeprefix("pedit_goal_")
    response = await api_client.update_relationship_goal(callback.from_user.id, goal)
    if not response.get("success"):
        await callback.message.answer(_profile_error_text(response))
        return
    await callback.message.answer(
        texts.PROFILE_GOAL_UPDATED, reply_markup=get_profile_edit_keyboard()
    )


# === СМЕНА ПЕРСОНАЖА (из личного кабинета, с предупреждением) === #

@handle_resolver_errors
async def resolve_edit_mask_request(callback: CallbackQuery, state: FSMContext):
    """Показ меню выбора персонажа: грузим доступные маски, сохраняем их в state"""
    await callback.answer()
    response = await api_client.get_user_stats(callback.from_user.id)
    if not response or not response.get("success"):
        await callback.message.answer(texts.LK_LOAD_ERROR, reply_markup=get_menu_keyboard())
        return
    masks = response.get("data", {}).get("available_masks", [])
    await state.update_data(available_masks=masks)
    await callback.message.answer(
        texts.MASK_SELECT_MENU, reply_markup=get_mask_select_keyboard(masks)
    )


@handle_resolver_errors
async def resolve_edit_mask_pick(callback: CallbackQuery, state: FSMContext):
    """Выбран персонаж — показываем предупреждение об утере истории"""
    await callback.answer()
    masks = (await state.get_data()).get("available_masks", [])
    idx = int(callback.data.removeprefix("mask_pick_"))
    if idx >= len(masks):
        return
    await state.update_data(pending_mask=masks[idx])
    await callback.message.answer(
        texts.MASK_CHANGE_WARNING, reply_markup=get_mask_confirm_keyboard()
    )


@handle_resolver_errors
async def resolve_edit_mask_confirm(callback: CallbackQuery, state: FSMContext):
    """Подтверждена смена персонажа — отправляем запрос"""
    await callback.answer()
    mask_name = (await state.get_data()).get("pending_mask")
    if not mask_name:
        await callback.message.answer(texts.PROFILE_UNKNOWN_ERROR)
        return
    response = await api_client.update_mask(callback.from_user.id, mask_name)
    if not response.get("success"):
        await callback.message.answer(_profile_error_text(response))
        return
    await callback.message.answer(
        texts.MASK_CHANGED_SUCCESS, reply_markup=get_profile_edit_keyboard()
    )


@handle_resolver_errors
async def resolve_mask_cancel(callback: CallbackQuery, state: FSMContext):
    """Отказ от смены персонажа — возврат в меню редактирования"""
    await resolve_profile_edit_menu(callback, state)


@handle_resolver_errors
async def resolve_mask_create(callback: CallbackQuery):
    """Кнопка «Создать Компаньона» — функция пока недоступна"""
    await callback.answer()
    await callback.message.answer(texts.MASK_CREATE_UNAVAILABLE)
