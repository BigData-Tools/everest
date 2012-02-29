"""
This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Configurators for the various subsystems of :mod:`everest`.

Created on Jun 22, 2011.
"""

from everest.entities.interfaces import IEntity
from everest.entities.system import Message
from everest.interfaces import IMessage
from everest.interfaces import IRepository
from everest.interfaces import IRepositoryManager
from everest.interfaces import IResourceUrlConverter
from everest.mime import AtomMime
from everest.mime import CsvMime
from everest.mime import XmlMime
from everest.querying.base import EXPRESSION_KINDS
from everest.querying.filtering import CqlFilterSpecificationVisitor
from everest.querying.filtering import EvalFilterSpecificationVisitor
from everest.querying.filtering import FilterSpecificationBuilder
from everest.querying.filtering import FilterSpecificationDirector
from everest.querying.filtering import SqlFilterSpecificationVisitor
from everest.querying.interfaces import IFilterSpecificationBuilder
from everest.querying.interfaces import IFilterSpecificationDirector
from everest.querying.interfaces import IFilterSpecificationFactory
from everest.querying.interfaces import IFilterSpecificationVisitor
from everest.querying.interfaces import IOrderSpecificationBuilder
from everest.querying.interfaces import IOrderSpecificationDirector
from everest.querying.interfaces import IOrderSpecificationFactory
from everest.querying.interfaces import IOrderSpecificationVisitor
from everest.querying.ordering import CqlOrderSpecificationVisitor
from everest.querying.ordering import EvalOrderSpecificationVisitor
from everest.querying.ordering import OrderSpecificationBuilder
from everest.querying.ordering import OrderSpecificationDirector
from everest.querying.ordering import SqlOrderSpecificationVisitor
from everest.querying.specifications import FilterSpecificationFactory
from everest.querying.specifications import OrderSpecificationFactory
from everest.repository import REPOSITORIES
from everest.repository import as_repository
from everest.representers.atom import AtomResourceRepresenter
from everest.representers.csv import CsvResourceRepresenter
from everest.representers.interfaces import IDataElementRegistry
from everest.representers.interfaces import IRepresenter
from everest.representers.xml import XmlResourceRepresenter
from everest.resources.base import Collection
from everest.resources.base import Resource
from everest.resources.interfaces import ICollectionResource
from everest.resources.interfaces import IMemberResource
from everest.resources.interfaces import IService
from everest.resources.repository import RepositoryManager
from everest.resources.service import Service
from everest.resources.system import MessageMember
from everest.url import ResourceUrlConverter
from repoze.bfg.configuration import Configurator as BfgConfigurator
from repoze.bfg.interfaces import IRequest
from repoze.bfg.path import caller_package
from zope.interface import alsoProvides as also_provides # pylint: disable=E0611,F0401
from zope.interface import classImplements as class_implements # pylint: disable=E0611,F0401
from zope.interface import providedBy as provided_by # pylint: disable=E0611,F0401

__docformat__ = 'reStructuredText en'
__all__ = ['Configurator',
           ]


class Configurator(BfgConfigurator):
    """
    Configurator for everest.
    """

    def __init__(self,
                 registry=None,
                 package=None,
                 # Entity level services.
                 filter_specification_factory=None,
                 order_specification_factory=None,
                 # Application level services.
                 service=None,
                 filter_builder=None,
                 filter_director=None,
                 cql_filter_specification_visitor=None,
                 sql_filter_specification_visitor=None,
                 eval_filter_specification_visitor=None,
                 order_builder=None,
                 order_director=None,
                 cql_order_specification_visitor=None,
                 sql_order_specification_visitor=None,
                 eval_order_specification_visitor=None,
                 url_converter=None,
                 **kw
                 ):
        if package is None:
            package = caller_package()
        BfgConfigurator.__init__(self,
                                 registry=registry, package=package, **kw)
        if registry is None:
            self.__setup(filter_specification_factory,
                         order_specification_factory,
                         service,
                         filter_builder,
                         filter_director,
                         cql_filter_specification_visitor,
                         sql_filter_specification_visitor,
                         eval_filter_specification_visitor,
                         order_builder,
                         order_director,
                         cql_order_specification_visitor,
                         sql_order_specification_visitor,
                         eval_order_specification_visitor,
                         url_converter)

    def get_registered_utility(self, *args, **kw):
        """
        Convenience method for obtaining a utility from the registry.
        """
        return self.registry.getUtility(*args, **kw) # pylint: disable=E1103

    def query_registered_utilities(self, *args, **kw):
        """
        Convenience method for querying a utility from the registry.
        """
        return self.registry.queryUtility(*args, **kw) # pylint: disable=E1103

    def setup_registry(self,
                       filter_specification_factory=None,
                       order_specification_factory=None,
                       service=None,
                       filter_specification_builder=None,
                       filter_specification_director=None,
                       cql_filter_specification_visitor=None,
                       sql_filter_specification_visitor=None,
                       eval_filter_specification_visitor=None,
                       order_specification_builder=None,
                       order_specification_director=None,
                       cql_order_specification_visitor=None,
                       sql_order_specification_visitor=None,
                       eval_order_specification_visitor=None,
                       url_converter=None,
                       **kw):
        BfgConfigurator.setup_registry(self, **kw)
        self.__setup(filter_specification_factory,
                     order_specification_factory,
                     service,
                     filter_specification_builder,
                     filter_specification_director,
                     cql_filter_specification_visitor,
                     sql_filter_specification_visitor,
                     eval_filter_specification_visitor,
                     order_specification_builder,
                     order_specification_director,
                     cql_order_specification_visitor,
                     sql_order_specification_visitor,
                     eval_order_specification_visitor,
                     url_converter)

    def add_orm_repository(self, name=None, entity_store_class=None,
                           aggregate_class=None,
                           make_default=False, configuration=None, _info=u''):
        if configuration is None:
            configuration = {}
        setting_info = [('db_string', 'db_string')]
        configuration.update(self.__cnf_from_settings(setting_info))
        self.__add_repository(name, REPOSITORIES.ORM, entity_store_class,
                              aggregate_class, make_default, configuration)

    def add_filesystem_repository(self, name=None, entity_store_class=None,
                                  aggregate_class=None,
                                  make_default=False, configuration=None,
                                  _info=u''):
        if configuration is None:
            configuration = {}
        setting_info = [('directory', 'fs_directory'),
                        ('content_type', 'fs_contenttype')]
        configuration.update(self.__cnf_from_settings(setting_info))
        self.__add_repository(name, REPOSITORIES.FILE_SYSTEM,
                              entity_store_class, aggregate_class,
                              make_default, configuration)

    def add_memory_repository(self, name=None, entity_store_class=None,
                              aggregate_class=None,
                              make_default=False, configuration=None,
                              _info=u''):
        if configuration is None:
            configuration = {}
        self.__add_repository(name, REPOSITORIES.MEMORY, entity_store_class,
                              aggregate_class, make_default, configuration)

    def add_resource(self, interface, member, entity,
                     collection=None,
                     collection_root_name=None, collection_title=None,
                     expose=True, repository=None, _info=u''):
        if not (isinstance(member, type)
                and IMemberResource in provided_by(object.__new__(member))):
            raise ValueError('The member must be a class that implements '
                             'IMemberResource.')
        if member.relation is None:
            raise ValueError('The member class must have a "relation" '
                             'attribute.')
        if not (isinstance(entity, type)
                and IEntity in provided_by(object.__new__(entity))):
            raise ValueError('The entity must be a class that implements '
                             'IEntity.')
        # Configure or create the collection class.
        if collection is None:
            collection = type('%sCollection' % member.__name__,
                              (Collection,), {})
            if collection_title is None:
                collection.title = 'Collection of %s' % member.__name__
        elif not issubclass(collection, Collection):
            raise ValueError('The collection class must be a subclass '
                             'of Collection.')
        # Configure the repository adapter.
        repo_mgr = self.get_registered_utility(IRepositoryManager)
        if repository is None:
            repo = repo_mgr.get_default()
        else:
            repo = repo_mgr.get(repository)
            if repo is None:
                # Add a builtin repository on the fly. 
                repo_type = getattr(REPOSITORIES, repository, None)
                if repo_type is None:
                    raise ValueError('Unknown repository type "%s".'
                                     % repository)
                if repo_type == REPOSITORIES.MEMORY:
                    self.add_memory_repository()
                elif repo_type == REPOSITORIES.ORM:
                    self.add_orm_repository()
                elif repo_type == REPOSITORIES.FILE_SYSTEM:
                    self.add_filesystem_repository()
                else:
                    raise NotImplementedError()
                repo = repo_mgr.get(repository)
        # Override the root name and title the collection, if requested.
        if not collection_root_name is None:
            collection.root_name = collection_root_name
        if not collection_title is None:
            collection.title = collection_title
        if expose:
            srvc = self.query_registered_utilities(IService)
            if srvc is None:
                raise ValueError('Need a IService utility to expose a '
                                 'resource.')
            if collection.root_name is None:
                raise ValueError('To expose a collection resource in the '
                                 'service (=root), a root name is required.')
        # Register the entity instance -> member instance adapter.
        mb_factory = member.create_from_entity
        self._register_adapter(mb_factory, (interface,), IMemberResource,
                               info=_info)
        # Register adapter object implementing interface -> member class
        self._register_adapter(lambda obj: member,
                               required=(interface,),
                               provided=IMemberResource,
                               name='member-class',
                               info=_info)
        # Register adapter object implementing interface -> collection class
        self._register_adapter(lambda obj: collection,
                               required=(interface,),
                               provided=ICollectionResource,
                               name='collection-class',
                               info=_info)
        # Register adapter object implementing interface -> member class
        self._register_adapter(lambda obj: entity,
                               required=(interface,),
                               provided=IEntity,
                               name='entity-class',
                               info=_info)
        # Register utility interface -> member class
        self._register_utility(member, interface,
                               name='member-class', info=_info)
        # Register utility interface -> collection class
        self._register_utility(collection, interface,
                               name='collection-class', info=_info)
        # Register utility interface -> entity class
        self._register_utility(entity, interface,
                               name='entity-class', info=_info)
        # Attach the marker interface to the registered resource classes, if
        # necessary, so the instances will provide it.
        if not interface in provided_by(member):
            class_implements(member, interface)
        if not interface in provided_by(collection):
            class_implements(collection, interface)
        if not interface in provided_by(entity):
            class_implements(entity, interface)
        # This enables us to pass a class instead of
        # an interface or instance to the various adapters.
        also_provides(member, interface)
        also_provides(collection, interface)
        also_provides(entity, interface)
        # Register collection with the repository.
        repo.manage(collection)
        # Register adapter implementing interface -> repository.
        self._register_adapter(lambda obj: repo,
                               required=(interface,),
                               provided=IRepository,
                               info=_info)
        # Expose (=register with the service) if requested.
        if expose:
            srvc.register(interface)

    def add_representer(self, resource, content_type, configuration=None,
                        _info=u''):
        # If we were passed a class, instantiate it.
        if type(configuration) is type:
            configuration = configuration()
        # FIXME: Should we allow interfaces here? # pylint: disable=W0511
        if not issubclass(resource, Resource):
            raise ValueError('Representers can only be registered for classes '
                             'inheriting from the Resource base class.')
        # Register customized data element class for the representer
        # class registered for the given content type.
        utility_name = content_type.mime_string
        rpr_cls = self.get_registered_utility(IRepresenter, utility_name)
        de_reg = self.query_registered_utilities(IDataElementRegistry,
                                                 utility_name)
        if de_reg is None:
            # A sad attempt at providing a singleton that lives as long
            # as the associated (zope) registry: The first time this is
            # called with a fresh registry, a data element registry is
            # instantiated and then registered as a utility.
            de_reg = rpr_cls.make_data_element_registry()
            self._register_utility(de_reg, IDataElementRegistry,
                                   name=utility_name)
        de_cls = de_reg.create_data_element_class(resource, configuration)
        de_reg.set_data_element_class(de_cls)
        # Register adapter resource, MIME name -> representer.
        self._register_adapter(rpr_cls.create_from_resource,
                               (resource,),
                               IRepresenter,
                               name=utility_name,
                               info=_info)

    def initialize_repositories(self):
        for coll_cls in [util.component
                         for util in self.registry.getRegisteredUtilities() # pylint: disable=E1103
                         if util.name == 'collection-class']:
            repo = as_repository(coll_cls)
            if not repo.is_initialized:
                repo.initialize()

    def _register_utility(self, *args, **kw):
        return self.registry.registerUtility(*args, **kw) # pylint: disable=E1103

    def _register_adapter(self, *args, **kw):
        return self.registry.registerAdapter(*args, **kw) # pylint: disable=E1103

    def __setup(self,
                filter_specification_factory,
                order_specification_factory,
                service,
                filter_specification_builder,
                filter_specification_director,
                cql_filter_specification_visitor,
                sql_filter_specification_visitor,
                eval_filter_specification_visitor,
                order_specification_builder,
                order_specification_director,
                cql_order_specification_visitor,
                sql_order_specification_visitor,
                eval_order_specification_visitor,
                url_converter):
        # Set up the repository manager.
        repo_mgr = RepositoryManager()
        self._register_utility(repo_mgr, IRepositoryManager)
        # Set up the root MEMORY repository and set it as the default
        # for all resources that do not specify a repository.
        mem_repo = repo_mgr.new(REPOSITORIES.MEMORY,
                                name=REPOSITORIES.MEMORY)
        repo_mgr.set(REPOSITORIES.MEMORY, mem_repo, make_default=True)
        # Set up filter and order specification factories.
        if filter_specification_factory is None:
            filter_specification_factory = FilterSpecificationFactory()
        self._register_utility(filter_specification_factory,
                               IFilterSpecificationFactory)
        if order_specification_factory is None:
            order_specification_factory = OrderSpecificationFactory()
        self._register_utility(order_specification_factory,
                               IOrderSpecificationFactory)
        # Create builtin representers.
        self._register_utility(CsvResourceRepresenter,
                               IRepresenter,
                               name=CsvMime.mime_string)
        self._register_utility(XmlResourceRepresenter,
                               IRepresenter,
                               name=XmlMime.mime_string)
        self._register_utility(AtomResourceRepresenter,
                               IRepresenter,
                               name=AtomMime.mime_string)
        # Set up the service.
        if service is None:
            service = Service()
        self._register_utility(service, IService)
        # Set up filter and order specification builders, directors, visitors.
        if filter_specification_builder is None:
            filter_specification_builder = FilterSpecificationBuilder
        self._register_utility(filter_specification_builder,
                               IFilterSpecificationBuilder)
        if filter_specification_director is None:
            filter_specification_director = FilterSpecificationDirector
        self._register_utility(filter_specification_director,
                               IFilterSpecificationDirector)
        if cql_filter_specification_visitor is None:
            cql_filter_specification_visitor = CqlFilterSpecificationVisitor
        self._register_utility(cql_filter_specification_visitor,
                               IFilterSpecificationVisitor,
                              name=EXPRESSION_KINDS.CQL)
        if sql_filter_specification_visitor is None:
            sql_filter_specification_visitor = SqlFilterSpecificationVisitor
        self._register_utility(sql_filter_specification_visitor,
                               IFilterSpecificationVisitor,
                               name=EXPRESSION_KINDS.SQL)
        if eval_filter_specification_visitor is None:
            eval_filter_specification_visitor = EvalFilterSpecificationVisitor
        self._register_utility(eval_filter_specification_visitor,
                               IFilterSpecificationVisitor,
                               name=EXPRESSION_KINDS.EVAL)
        if order_specification_builder is None:
            order_specification_builder = OrderSpecificationBuilder
        self._register_utility(order_specification_builder,
                               IOrderSpecificationBuilder)
        if order_specification_director is None:
            order_specification_director = OrderSpecificationDirector
        self._register_utility(order_specification_director,
                               IOrderSpecificationDirector)
        if cql_order_specification_visitor is None:
            cql_order_specification_visitor = CqlOrderSpecificationVisitor
        self._register_utility(cql_order_specification_visitor,
                               IOrderSpecificationVisitor,
                               name=EXPRESSION_KINDS.CQL)
        if sql_order_specification_visitor is None:
            sql_order_specification_visitor = SqlOrderSpecificationVisitor
        self._register_utility(sql_order_specification_visitor,
                               IOrderSpecificationVisitor,
                               name=EXPRESSION_KINDS.SQL)
        if eval_order_specification_visitor is None:
            eval_order_specification_visitor = EvalOrderSpecificationVisitor
        self._register_utility(eval_order_specification_visitor,
                               IOrderSpecificationVisitor,
                               name=EXPRESSION_KINDS.EVAL)
        # URL converter adapter.
        if url_converter is None:
            url_converter = ResourceUrlConverter
        self._register_adapter(url_converter, (IRequest,),
                               IResourceUrlConverter)
        # Register system resources provided as a service to the application.
        self.add_resource(IMessage, MessageMember, Message,
                          repository=REPOSITORIES.MEMORY,
                          collection_root_name='_messages')

    def __add_repository(self, name, repo_type, ent_store_cls, agg_cls,
                         make_default, cnf):
        repo_mgr = self.get_registered_utility(IRepositoryManager)
        repo = repo_mgr.new(repo_type, name=name,
                            entity_store_class=ent_store_cls,
                            aggregate_class=agg_cls)
        repo.configure(**cnf)
        repo_mgr.set(name, repo, make_default=make_default)

    def __cnf_from_settings(self, setting_info):
        settings = self.get_settings()
        return dict([(name, settings.get(key))
                     for (name, key) in setting_info
                     if not settings.get(key, None) is None])

