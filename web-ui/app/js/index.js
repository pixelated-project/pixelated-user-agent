import 'js/lib/highlightRegex';
import 'js/monkey_patching/all';

import compose from 'flight/lib/compose';
import registry from 'flight/lib/registry';
import advice from 'flight/lib/advice';
import withLogging from 'flight/lib/logger';
import debug from 'flight/lib/debug';
import events from 'page/events';
import initializeDefault from 'page/default';

window.Pixelated = window.Pixelated || {};
window.Pixelated.events = events;

compose.mixin(registry, [advice.withAdvice, withLogging]);

debug.enable(true);
debug.events.logAll();

initializeDefault('');
