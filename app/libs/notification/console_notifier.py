from app import constants
from app.libs.notification.base import NotifierBase


class ConsoleNotifier(NotifierBase):
    """
        Notify that the scraping process is complete.

        Args:
            products_count (int): The total number of products scraped.
            updated_count (int): The number of products that were updated.

        Returns:
            None
    """

    def notify_scraping_complete(self, products_count: int, updated_count: int) -> None:
        print(
            constants.SUCCESS_NOTIFIER_MESSAGE.format(
                products_count=products_count, updated_count=updated_count
            )
        )
