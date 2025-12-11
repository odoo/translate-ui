# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from . import models
from . import tools


def pre_init_hook(env):
    logging.getLogger(__name__).warning("Pre-init hook: caches invalidated")
    env.invalidate_all()


def post_init_hook(env):
    logging.getLogger(__name__).warning("Post-init hook: reset all loaded translations")
    modules = env['ir.module.module'].search([])
    modules._update_translations(overwrite=True)
