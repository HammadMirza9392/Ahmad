"""
CMS Controller
Handles public website page rendering.
"""
from app.services.cms_service import CMSService
from app.services.department_service import DepartmentService


class CMSController:

    @staticmethod
    def get_page_data(slug):
        """Retrieve page and related data for rendering."""
        page = CMSService.get_by_slug(slug)
        if not page or not page.is_published:
            return None
        return page

    @staticmethod
    def get_home_data():
        """Data for the home page."""
        departments = DepartmentService.get_all(active_only=True)
        news = CMSService.get_news(page=1, per_page=6)
        events = CMSService.get_events(page=1, per_page=4)
        return {
            'departments': departments,
            'news': news.items if news else [],
            'events': events.items if events else [],
        }

    @staticmethod
    def get_menu():
        return CMSService.get_menu_pages()
