from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    bot_token: str = Field(alias='BOT_TOKEN')
    admin_telegram_ids: str = Field(default='', alias='ADMIN_TELEGRAM_IDS')
    panel_base_url: str = Field(alias='PANEL_BASE_URL')
    panel_api_token: str = Field(alias='PANEL_API_TOKEN')
    panel_sub_base_url: str = Field(alias='PANEL_SUB_BASE_URL')
    inbound_direct_id: int = Field(default=40, alias='INBOUND_DIRECT_ID')
    inbound_tunnel_id: int = Field(default=41, alias='INBOUND_TUNNEL_ID')
    payment_card_number: str = Field(alias='PAYMENT_CARD_NUMBER')
    payment_card_holder: str = Field(default='', alias='PAYMENT_CARD_HOLDER')
    database_url: str = Field(alias='DATABASE_URL')
    api_port: int = Field(default=8000, alias='API_PORT')
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')
    timezone: str = Field(default='Asia/Tehran', alias='TIMEZONE')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore', populate_by_name=True)

    @property
    def admin_ids(self) -> set[int]:
        return {int(x.strip()) for x in self.admin_telegram_ids.split(',') if x.strip()}

settings = Settings()
