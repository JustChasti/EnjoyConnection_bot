"""Клавиатуры для обработчиков"""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from config.config import PLAN_LABELS, MASK_SLOTS_COUNT
from config import texts

def get_back_to_admin_menu_keyboard():
    """Клавиатура с кнопкой 'Назад в меню'"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад в меню", callback_data="admin_back_to_menu")]
    ])


def get_menu_keyboard():
    """Постоянная подклавиатурная кнопка Меню"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Меню 📊")]],
        resize_keyboard=True,
        input_field_placeholder="Напиши что-нибудь..."
    )


def get_admin_menu_keyboard():
    """Клавиатура с админскими кнопками"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить профиль user_id", callback_data="admin_user_info")],
        [InlineKeyboardButton(text="Изменить настройки user_id", callback_data="admin_set_options")],
        [InlineKeyboardButton(text="User_id всех пользователей", callback_data="admin_all_users")],
        [InlineKeyboardButton(text="Удалить пользователя", callback_data="admin_delete_user")],
        [InlineKeyboardButton(text="Создать промокод", callback_data="admin_create_promo")],
        [InlineKeyboardButton(text="Отправить сообщение", callback_data="admin_send_message")],
        [InlineKeyboardButton(text="Массовая рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="Выход", callback_data="admin_exit")]
    ])


def get_subscription_keyboard(prices: dict) -> InlineKeyboardMarkup:
    """Клавиатура выбора плана подписки"""
    buttons = []
    for plan, label in PLAN_LABELS.items():
        sub = prices.get(plan)
        if sub:
            buttons.append([
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"sub_plan_{plan}"
                )
            ])
    buttons.append([
        InlineKeyboardButton(text="Отмена", callback_data="sub_cancel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_method_keyboard(plan: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора способа оплаты (пока только Stars)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Оплатить звёздами ⭐",
                callback_data=f"sub_pay_stars_{plan}"
            )
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="sub_back_to_plans")
        ],
    ])


def get_lk_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура личного кабинета"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Показать прогресс отношений", callback_data="menu_relationship")
        ],
        [InlineKeyboardButton(text="Редактировать профиль", callback_data="profile_edit")],
        [InlineKeyboardButton(text="Ввести промокод", callback_data="menu_promo")],
        [InlineKeyboardButton(text="Купить подписку", callback_data="menu_buy")],
    ])


# === ПРОФИЛЬ / АНКЕТА === #

def get_profile_anketa_keyboard() -> InlineKeyboardMarkup:
    """Предложение заполнить профиль после первого сообщения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить", callback_data="profile_fill")],
        [InlineKeyboardButton(text="Пропустить", callback_data="profile_skip")],
    ])


def get_profile_edit_keyboard() -> InlineKeyboardMarkup:
    """Меню редактирования профиля"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Возраст", callback_data="pedit_age")],
        [InlineKeyboardButton(text="Пол", callback_data="pedit_gender")],
        [InlineKeyboardButton(text="Цель общения", callback_data="pedit_goal")],
        [InlineKeyboardButton(text="Сменить Персонажа", callback_data="pedit_mask")],
        [InlineKeyboardButton(text="Назад", callback_data="pedit_to_lk")],
    ])


def get_mask_select_keyboard(available_masks: list[str]) -> InlineKeyboardMarkup:
    """Меню выбора персонажа в личном кабинете.

    Первые слоты занимают доступные маски, остальные до MASK_SLOTS_COUNT —
    кнопки «Создать Компаньона». В callback_data маски кладётся индекс (лимит
    callback_data — 64 байта, а имена компаньонов могут быть длинными), само имя
    берётся из available_masks, сохранённых в FSM.
    """
    buttons = []
    for i in range(MASK_SLOTS_COUNT):
        if i < len(available_masks):
            buttons.append([InlineKeyboardButton(
                text=available_masks[i], callback_data=f"mask_pick_{i}")])
        else:
            buttons.append([InlineKeyboardButton(
                text=texts.MASK_CREATE_BUTTON, callback_data="mask_create")])
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="pedit_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_survey_mask_keyboard() -> InlineKeyboardMarkup:
    """Выбор персонажа в первичной анкете (две фиксированные маски, без генерации)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Джой", callback_data="mask_goal_Joi")],
        [InlineKeyboardButton(text="Грей", callback_data="mask_goal_Gray")],
    ])


def get_mask_confirm_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение смены персонажа (с потерей истории)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="mask_confirm")],
        [InlineKeyboardButton(text="Нет", callback_data="mask_cancel")],
    ])


def get_survey_gender_keyboard() -> InlineKeyboardMarkup:
    """Выбор пола в пошаговой анкете"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я мужчина", callback_data="survey_gender_male")],
        [InlineKeyboardButton(text="Я женщина", callback_data="survey_gender_female")],
    ])


def get_survey_goal_keyboard() -> InlineKeyboardMarkup:
    """Выбор цели общения в пошаговой анкете"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Лучшие друзья", callback_data="survey_goal_best_friend")],
        [InlineKeyboardButton(
            text="Романтические партнёры", callback_data="survey_goal_romantic")
        ],
    ])


def get_edit_gender_keyboard() -> InlineKeyboardMarkup:
    """Выбор пола при редактировании профиля"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я мужчина", callback_data="pedit_gender_male")],
        [InlineKeyboardButton(text="Я женщина", callback_data="pedit_gender_female")],
        [InlineKeyboardButton(text="Назад", callback_data="pedit_back")],
    ])


def get_edit_goal_keyboard() -> InlineKeyboardMarkup:
    """Выбор цели общения при редактировании профиля"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Лучшие друзья", callback_data="pedit_goal_best_friend")],
        [InlineKeyboardButton(
            text="Романтические партнёры", callback_data="pedit_goal_romantic")
        ],
        [InlineKeyboardButton(text="Назад", callback_data="pedit_back")],
    ])


def get_edit_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка Назад для экрана ввода возраста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="pedit_back")],
    ])
