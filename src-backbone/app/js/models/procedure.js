const ACTIVE_PAGE_CHANGE_EVENT = 'change:activePage';
const Config = require('utils/config');

let App     = require('utils/sanaAppInstance');
let Helpers = require('utils/helpers');
let Pages   = require('collections/pages');
let Page    = require('./page');


let Procedure = Backbone.Model.extend({

    urlRoot: '/api/procedures',

    defaults: function() {
        let user = App().session.user;

        // These values are only used when we POST /procedures a new procedure
        return {
            'title': i18n.t('Untitled Procedure'),
            'author': user.get('first_name') + ' ' + user.get('last_name'),
        };
    },

    constructor: function(attributes, options = {}) {
        // We do not want the Collection to be an attribute of this model because:
        // - parse() is called before initialize()/defaults() but we need a common reference to the Pages
        // - creating a new Pages inside parse every time causes a lot of headache with event listeners and garbage collection
        // - we'd need to override toJSON() anyways to only return the list of ids
        this.pages = new Pages(null, { parentProcedure: this });

        if (options.activePageId) {
            this.activePageId = parseInt(options.activePageId);
            delete options.activePageId;
        }

        // Propagate AJAX events from child to this model so that the status bar can be notified
        this.listenTo(this.pages, 'add', function(model, collection, options) {
            Helpers.propagateEvents(model, this);
        });
        this.listenTo(this.pages, 'reset', function(collection, options) {
            for (let model of collection.models) {
                Helpers.propagateEvents(model, this);
            }
        });

        options.parse = true;
        Backbone.Model.prototype.constructor.call(this, attributes, options);
    },

    parse: function(response, options) {
        if (_.has(response, 'created')) {
            response.created = new Date(Date.parse(response.created));
        }

        if (_.has(response, 'last_modified')) {
            response.last_modified = new Date(Date.parse(response.last_modified));
        }

        this._setPages(response.pages);
        delete response.pages;

        return response;
    },

    toJSON: function() {
        let json = _.clone(this.attributes);
        json.pages = this.pages.pluck('id');
        return json;
    },

    _setPages: function (pages) {
        this.pages.reset(pages, { parse: true });

        let activePage = this.pages.findWhere(function(page) {
            return page.isActive();
        });

        if (activePage) {
            this.selectActivePage(activePage);
        }
    },

    //--------------------------------------------------------------------------
    // Managing activePageId
    //--------------------------------------------------------------------------

    selectActivePage: function(page) {
        this.activePageId = page.get('id');
        this.trigger(ACTIVE_PAGE_CHANGE_EVENT, page);
    },

    unselectActivePage: function() {
        this.activePageId = undefined;
        this.trigger(ACTIVE_PAGE_CHANGE_EVENT, null);
    },

    getActivePage: function() {
        return this.pages.get(this.activePageId);
    },

    //--------------------------------------------------------------------------
    // View events
    //--------------------------------------------------------------------------

    createNewPage: function() {
        let position = 0;
        if (!_.isEmpty(this.pages.models)) {
            let lastPage = _.max(this.pages.models, page => page.get('display_index'));
            position = lastPage.get('display_index') + 1;
        }

        let page = new Page({
            display_index: position,
            procedure: this.get('id'),
        });

        let self = this;
        page.save({}, {
            success: function() {
                console.info('Created Page', page.get('id'));
                self.pages.add(page);
                self.selectActivePage(page);
            },
            error: function() {
                console.warn('Failed to create Page', page.get('id'));
                App().RootView.showNotification('Failed to create Page!');
            },
        });
    },

    generate: function() {
        const title = this.get('title');
        $.ajax({
            type: 'GET',
            url: this.url() + '/generate',
            success: function onGenerateSuccess(data, status, jqXHR) {
                const filename = title + '.xml';
                Helpers.downloadXMLFile(data, filename);
            },
            error: function onGenerateError(jqXHR, textStatus, errorThrown) {
                console.warn('Failed to generate Procedure', textStatus);
                App().RootView.showNotification({
                    title: i18n.t('Failed to generate Procedure', { procedureTitle: title }),
                    desc: i18n.t(jqXHR.responseText),
                }, {
                    isTranslated: true
                });
            },
        });
    },

    generateGraph: function() {
        const nodes = [];
        const edges = [];

        // const conditionalNodes = [];

        const pages = this.pages;

        if (pages.length > 0) {
            nodes.push(pages.at(0));
            for (let i = 1; i < pages.length; i++) {
                const prevPage = pages.at(i - 1);
                const curPage = pages.at(i);
                nodes.push(curPage);

                edges.push([i - 1, i]);

                const showIfs = curPage.showIfs.models;
                for (let showIf of showIfs) {
                    const rootConditionalNode = showIf.rootConditionalNode;
                    const allConditionNodes = this._getChildrenConditionalNodes(rootConditionalNode);
                    // conditionalNodes.push({curPage, allConditionNodes});

                    for (let node of allConditionNodes) {
                        const criteriaElement = node.get('criteria_element');
                        if (criteriaElement && criteriaElement >= 0) {
                            const {pageIndex, elementIndex} = this._findElement(criteriaElement);
                            edges.push([pageIndex, i]);
                        }
                    }
                }
            }
        }

        return {
            nodes, 
            edges,
            // conditionalNodes
        };
    },

    _findElement: function(id) {
        for (let i = 0; i < this.pages.length; i++) {
            const page = this.pages.at(i);

            for (let j = 0; j < page.elements.length; j++) {
                const element = page.elements.at(j);
                if (element.id === id) {
                    return {
                        pageIndex: i, 
                        elementIndex: j
                    };
                }
            }
        }
        return {pageIndex: -1, elementIndex: -1};
    },

    _getChildrenConditionalNodes: function(node) {
        const nodes = [node];

        const children = node.childrenNodes.models;
        for (let child of children) {
            nodes.push(...this._getChildrenConditionalNodes(child));
        }
        return nodes;
    },
});

Procedure.ACTIVE_PAGE_CHANGE_EVENT = ACTIVE_PAGE_CHANGE_EVENT;

module.exports = Procedure;
