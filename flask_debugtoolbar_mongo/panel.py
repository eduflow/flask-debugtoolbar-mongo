from pymongo_basic_profiler import OpTracker

from flask_debugtoolbar.panels import DebugPanel
import jinja2
from . import jinja_filters


class MongoDebugPanel(DebugPanel):
    """Panel that shows information about MongoDB operations.
    """

    name = 'MongoDB'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(MongoDebugPanel, self).__init__(*args, **kwargs)
        self.operation_tracker = OpTracker()
        self.jinja_env.loader = jinja2.ChoiceLoader(
            [
                self.jinja_env.loader,
                jinja2.PrefixLoader(
                    {'debug_tb_mongo': jinja2.PackageLoader(__name__, 'templates')}
                ),
            ]
        )
        filters = (
            'format_stack_trace',
            'embolden_file',
            'format_dict',
            'highlight',
            'pluralize',
        )
        for jfilter in filters:
            self.jinja_env.filters[jfilter] = getattr(jinja_filters, jfilter)

        self.operation_tracker.install_tracker()

    def process_request(self, request):
        self.operation_tracker.reset()

    def nav_title(self):
        return 'MongoDB'

    def nav_subtitle(self):
        fun = lambda x, y: (x, len(y), '%.2f' % sum(z['time'] for z in y))
        ctx = {'operations': [], 'count': 0, 'time': 0}

        if self.operation_tracker.queries:
            ctx['operations'].append(fun('read', self.operation_tracker.queries))
            ctx['count'] += len(self.operation_tracker.queries)
            ctx['time'] += sum(x['time'] for x in self.operation_tracker.queries)

        if self.operation_tracker.inserts:
            ctx['operations'].append(fun('insert', self.operation_tracker.inserts))
            ctx['count'] += len(self.operation_tracker.inserts)
            ctx['time'] += sum(x['time'] for x in self.operation_tracker.inserts)

        if self.operation_tracker.updates:
            ctx['operations'].append(fun('update', self.operation_tracker.updates))
            ctx['count'] += len(self.operation_tracker.updates)
            ctx['time'] += sum(x['time'] for x in self.operation_tracker.updates)

        if self.operation_tracker.removes:
            ctx['operations'].append(fun('delete', self.operation_tracker.removes))
            ctx['count'] += len(self.operation_tracker.removes)
            ctx['time'] += sum(x['time'] for x in self.operation_tracker.removes)

        ctx['time'] = '%.2f' % ctx['time']
        return self.render('debug_tb_mongo/mongo-panes-subtitle.html', ctx)

    def title(self):
        return 'MongoDB Operations'

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        context['queries'] = self.operation_tracker.queries
        context['inserts'] = self.operation_tracker.inserts
        context['updates'] = self.operation_tracker.updates
        context['removes'] = self.operation_tracker.removes
        return self.render('debug_tb_mongo/mongo-panel.html', context)
