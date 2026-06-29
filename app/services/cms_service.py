"""
CMS Service
Manages static website pages and their sections.
"""
from app import db
from app.models.cms import CMSPage, CMSSection
from app.models.news import News
from app.models.event import Event
from app.models.faq import FAQ
from app.models.gallery import GalleryAlbum
from app.utils.helpers import generate_slug


class CMSService:

    # ───────────── PAGES ─────────────

    @staticmethod
    def get_all_pages():
        return CMSPage.query.order_by(CMSPage.menu_order).all()

    @staticmethod
    def get_menu_pages():
        return CMSPage.query.filter_by(is_published=True, show_in_menu=True).order_by(
            CMSPage.menu_order
        ).all()

    @staticmethod
    def get_by_slug(slug):
        return CMSPage.query.filter_by(slug=slug).first()

    @staticmethod
    def get_by_id(page_id):
        return db.session.get(CMSPage, page_id)

    @staticmethod
    def create_page(data, user_id=None):
        page = CMSPage(
            title=data['title'],
            slug=data.get('slug') or generate_slug(data['title']),
            content=data.get('content', ''),
            meta_title=data.get('meta_title'),
            meta_description=data.get('meta_description'),
            page_type=data.get('page_type', 'custom'),
            banner_image=data.get('banner_image'),
            is_published=data.get('is_published', True),
            show_in_menu=data.get('show_in_menu', True),
            menu_order=data.get('menu_order', 0),
            parent_id=data.get('parent_id'),
            created_by=user_id,
        )
        db.session.add(page)
        db.session.commit()
        return page

    @staticmethod
    def update_page(page, data):
        for field in ['title', 'content', 'meta_title', 'meta_description', 'page_type',
                       'banner_image', 'is_published', 'show_in_menu', 'menu_order', 'parent_id']:
            if field in data:
                setattr(page, field, data[field])
        if 'slug' in data and data['slug']:
            page.slug = data['slug']
        db.session.commit()
        return page

    @staticmethod
    def delete_page(page):
        db.session.delete(page)
        db.session.commit()

    # ───────────── SECTIONS ─────────────

    @staticmethod
    def get_section(section_id):
        return db.session.get(CMSSection, section_id)

    @staticmethod
    def add_section(page_id, data):
        section = CMSSection(
            page_id=page_id,
            section_key=data['section_key'],
            title=data.get('title'),
            content=data.get('content'),
            image=data.get('image'),
            extra_data=data.get('extra_data'),
            sort_order=data.get('sort_order', 0),
            is_visible=data.get('is_visible', True),
        )
        db.session.add(section)
        db.session.commit()
        return section

    @staticmethod
    def update_section(section, data):
        for field in ['title', 'content', 'image', 'extra_data', 'sort_order', 'is_visible']:
            if field in data:
                setattr(section, field, data[field])
        db.session.commit()
        return section

    @staticmethod
    def delete_section(section):
        db.session.delete(section)
        db.session.commit()

    # ───────────── NEWS ─────────────

    @staticmethod
    def get_news(page=1, per_page=10, published_only=True):
        q = News.query.order_by(News.published_at.desc())
        if published_only:
            q = q.filter_by(is_published=True)
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_news_by_slug(slug):
        return News.query.filter_by(slug=slug).first()

    @staticmethod
    def create_news(data, user_id=None):
        article = News(
            title=data['title'],
            slug=data.get('slug') or generate_slug(data['title']),
            excerpt=data.get('excerpt'),
            content=data.get('content'),
            image=data.get('image'),
            category=data.get('category'),
            department_id=data.get('department_id'),
            is_published=data.get('is_published', True),
            is_featured=data.get('is_featured', False),
            created_by=user_id,
        )
        db.session.add(article)
        db.session.commit()
        return article

    @staticmethod
    def update_news(article, data):
        for field in ['title', 'excerpt', 'content', 'image', 'category',
                       'department_id', 'is_published', 'is_featured']:
            if field in data:
                setattr(article, field, data[field])
        if 'slug' in data and data['slug']:
            article.slug = data['slug']
        db.session.commit()
        return article

    @staticmethod
    def delete_news(article):
        db.session.delete(article)
        db.session.commit()

    # ───────────── EVENTS ─────────────

    @staticmethod
    def get_events(page=1, per_page=10, active_only=True):
        q = Event.query.order_by(Event.event_date.desc())
        if active_only:
            q = q.filter_by(is_active=True)
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_event_by_slug(slug):
        return Event.query.filter_by(slug=slug).first()

    @staticmethod
    def create_event(data, user_id=None):
        event = Event(
            title=data['title'],
            slug=data.get('slug') or generate_slug(data['title']),
            description=data.get('description'),
            content=data.get('content'),
            image=data.get('image'),
            venue=data.get('venue'),
            event_date=data.get('event_date'),
            end_date=data.get('end_date'),
            department_id=data.get('department_id'),
            is_featured=data.get('is_featured', False),
            created_by=user_id,
        )
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def update_event(event, data):
        for field in ['title', 'description', 'content', 'image', 'venue',
                       'event_date', 'end_date', 'department_id', 'is_active', 'is_featured']:
            if field in data:
                setattr(event, field, data[field])
        if 'slug' in data and data['slug']:
            event.slug = data['slug']
        db.session.commit()
        return event

    @staticmethod
    def delete_event(event):
        db.session.delete(event)
        db.session.commit()

    # ───────────── FAQS ─────────────

    @staticmethod
    def get_faqs(active_only=True, department_id=None):
        q = FAQ.query.order_by(FAQ.sort_order)
        if active_only:
            q = q.filter_by(is_active=True)
        if department_id:
            q = q.filter_by(department_id=department_id)
        return q.all()

    @staticmethod
    def create_faq(data):
        faq = FAQ(
            question=data['question'],
            answer=data['answer'],
            category=data.get('category'),
            department_id=data.get('department_id'),
            sort_order=data.get('sort_order', 0),
        )
        db.session.add(faq)
        db.session.commit()
        return faq

    @staticmethod
    def update_faq(faq, data):
        for field in ['question', 'answer', 'category', 'department_id', 'sort_order', 'is_active']:
            if field in data:
                setattr(faq, field, data[field])
        db.session.commit()
        return faq

    @staticmethod
    def delete_faq(faq):
        db.session.delete(faq)
        db.session.commit()

    # ───────────── GALLERY ─────────────

    @staticmethod
    def get_albums(active_only=True, department_id=None):
        q = GalleryAlbum.query.order_by(GalleryAlbum.sort_order)
        if active_only:
            q = q.filter_by(is_active=True)
        if department_id:
            q = q.filter_by(department_id=department_id)
        return q.all()

    @staticmethod
    def get_album_by_id(album_id):
        return db.session.get(GalleryAlbum, album_id)
