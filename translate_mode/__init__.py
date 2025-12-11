# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from . import models
from . import tools


_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    _logger.warning("Pre-init hook: caches invalidated")
    env.invalidate_all()


def post_init_hook(env):
    langs = env['res.lang'].get_installed()
    filter_lang = [code for code, _ in langs]
    mod_names = [name for name in env['ir.module.module']._installed()]
    _logger.warning(f"Post-init hook: updating translations for langs {filter_lang} for modules {mod_names}")
    env['ir.module.module']._load_module_terms(mod_names, filter_lang, overwrite=True)
