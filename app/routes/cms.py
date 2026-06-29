"""
CMS Routes
Public-facing website pages — home, about, departments, contact, etc.
"""
from flask import Blueprint, render_template, abort, request

from app.controllers.cms_controller import CMSController
from app.services.cms_service import CMSService
from app.services.department_service import DepartmentService
from app.services.download_service import DownloadService

cms_bp = Blueprint('cms', __name__)


@cms_bp.context_processor
def inject_menu():
    return {'cms_menu': CMSController.get_menu()}


@cms_bp.route('/')
def home():
    data = CMSController.get_home_data()
    page = CMSService.get_by_slug('home')
    return render_template('cms/home.html', page=page, **data)


@cms_bp.route('/page/<slug>')
def page(slug):
    p = CMSController.get_page_data(slug)
    if not p:
        abort(404)

    # Special page types get their own template
    template_map = {
        'about': 'cms/about.html',
        'contact': 'cms/contact.html',
        'department': 'cms/departments.html',
    }
    template = template_map.get(p.page_type, 'cms/page.html')

    extra = {}
    req_page = request.args.get('page', 1, type=int)

    if p.page_type == 'department' or slug == 'departments':
        extra['departments'] = DepartmentService.get_all(active_only=True)
    if slug == 'faq':
        extra['faqs'] = CMSService.get_faqs()
    if slug == 'news':
        extra['news_list'] = CMSService.get_news(page=req_page, per_page=20)
    if slug == 'events':
        extra['events_list'] = CMSService.get_events(page=req_page, per_page=20)
    if slug == 'gallery':
        extra['albums'] = CMSService.get_albums()
    if slug == 'downloads':
        extra['downloads'] = DownloadService.get_all(page=req_page, per_page=50)
    if slug == 'admission':
        pass  # admission uses generic page content only

    return render_template(template, page=p, **extra)


@cms_bp.route('/department/<slug>')
def department_detail(slug):
    dept = DepartmentService.get_by_slug(slug)
    if not dept:
        abort(404)
    return render_template('cms/department_detail.html', dept=dept)
