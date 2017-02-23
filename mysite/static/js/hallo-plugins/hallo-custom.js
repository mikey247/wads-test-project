(function() {
    (function($) {
        return $.widget('IKS.superscriptbutton', {
            populateToolbar: function(toolbar) {
                var button, widget;
                widget = this;
                var getEnclosing = function(tag) {
                    var node = widget.options.editable.getSelection().commonAncestorContainer;
                    return $(node).parents(tag).get(0);
                };
                button = $('<span></span>');
                button.hallobutton({
                                    uuid: this.options.uuid,
                                    editable: this.options.editable,
                                    label: 'Superscript',
                                    icon: 'fa fa-superscript',
                                    command: null,
                                    queryState: function(event) {
                                        return button.hallobutton('checked', !!getEnclosing("sup"));
                                    }
                }); 
                toolbar.append(button);
                button.on('click', function(event) {
                    return widget.options.editable.execute(
                        getEnclosing("sup") ? 'removeFormat' : 'superscript');
                });
                }
        });
    })(jQuery);
}).call(this);

(function() {
    (function($) {
        return $.widget('IKS.subscriptbutton', {
            populateToolbar: function(toolbar) {
                var button, widget;
                widget = this;
                var getEnclosing = function(tag) {
                    var node = widget.options.editable.getSelection().commonAncestorContainer;
                    return $(node).parents(tag).get(0);
                };
                button = $('<span></span>');
                button.hallobutton({
                                    uuid: this.options.uuid,
                                    editable: this.options.editable,
                                    label: 'Subscript',
                                    icon: 'fa fa-subscript',
                                    command: null,
                                    queryState: function(event) {
                                        return button.hallobutton('checked', !!getEnclosing("sub"));
                                    }
                }); 
                toolbar.append(button);
                button.on('click', function(event) {
                    return widget.options.editable.execute(
                        getEnclosing("sub") ? 'removeFormat' : 'sub' );
                });
                }
        });
    })(jQuery);
}).call(this);

(function() {
    (function($) {
        return $.widget('IKS.codebutton', {
            options: {
                uuid: '',
                editable: null
            },
            populateToolbar: function(toolbar) {
                var button, widget;
                widget = this;

                var getEnclosing = function(tag) {
                    var node = widget.options.editable.getSelection().commonAncestorContainer;
                    return $(node).parents(tag).get(0);
                };

                button = $('<span></span>');
                button.hallobutton({
                    uuid: this.options.uuid,
                    editable: this.options.editable,
                    label: 'Code Span',
                    icon: 'fa fa-code',
                    command: null,
		    queryState: function(event) {
			return button.hallobutton('checked', !!getEnclosing("code"));
		    }
                });
 
                toolbar.append(button);
 
                button.on('click', function(event) {
		    lastSelection = widget.options.editable.getSelection();
		    has_ws_end = lastSelection.toString().endsWith(' ') ? ' ':''
		    if( getEnclosing("code") ) {
			return widget.options.editable.execute('removeFormat');
		    } else {
			alert('"'+lastSelection.toHtml()+'"');
			return widget.options.editable.execute('insertHTML', '<code>'+lastSelection.toHtml().trim()+'</code>'+has_ws_end);
		    }
                });
            }
        });
    })(jQuery);
}).call(this);

(function() {
    (function($) {
        return $.widget('IKS.kbdbutton', {
            options: {
                uuid: '',
                editable: null
            },
            populateToolbar: function(toolbar) {
                var button, widget;
                widget = this;

                var getEnclosing = function(tag) {
                    var node = widget.options.editable.getSelection().commonAncestorContainer;
                    return $(node).parents(tag).get(0);
                };

                button = $('<span></span>');
                button.hallobutton({
                    uuid: this.options.uuid,
                    editable: this.options.editable,
                    label: 'KBD Span',
                    icon: 'fa fa-keyboard',
                    command: null,
		    queryState: function(event) {
			return button.hallobutton('checked', !!getEnclosing("kbd"));
		    }
                });
 
                toolbar.append(button);
 
                button.on('click', function(event) {
		    lastSelection = widget.options.editable.getSelection();
		    has_ws_end = lastSelection.toString().endsWith(' ') ? ' ':''
		    if( getEnclosing("kbd") ) {
			return widget.options.editable.execute('removeFormat');
		    } else {
			return widget.options.editable.execute('insertHTML', '<kbd>'+lastSelection.toHtml().trim()+'</kbd>'+has_ws_end);
		    }
                });
            }
        });
    })(jQuery);
}).call(this);

(function() {
    (function($) {
        return $.widget('IKS.varbutton', {
            options: {
                uuid: '',
                editable: null
            },
            populateToolbar: function(toolbar) {
                var button, widget;
                widget = this;

                var getEnclosing = function(tag) {
                    var node = widget.options.editable.getSelection().commonAncestorContainer;
                    return $(node).parents(tag).get(0);
                };

                button = $('<span></span>');
                button.hallobutton({
                    uuid: this.options.uuid,
                    editable: this.options.editable,
                    label: 'Variable Span',
                    icon: 'fa fa-variable',
                    command: null,
		    queryState: function(event) {
			return button.hallobutton('checked', !!getEnclosing("var"));
		    }
                });
 
                toolbar.append(button);
 
                button.on('click', function(event) {
		    lastSelection = widget.options.editable.getSelection();
		    has_ws_end = lastSelection.toString().endsWith(' ') ? ' ':''
		    if( getEnclosing("var") ) {
			return widget.options.editable.execute('removeFormat');
		    } else {
			return widget.options.editable.execute('insertHTML', '<var>'+lastSelection.toHtml().trim()+'</var>'+has_ws_end);
		    }
                });
            }
        });
    })(jQuery);
}).call(this);

(function() {
    (function($) {
        return $.widget('IKS.sampbutton', {
            options: {
                uuid: '',
                editable: null
            },
            populateToolbar: function(toolbar) {
                var button, widget;
                widget = this;

                var getEnclosing = function(tag) {
                    var node = widget.options.editable.getSelection().commonAncestorContainer;
                    return $(node).parents(tag).get(0);
                };

                button = $('<span></span>');
                button.hallobutton({
                    uuid: this.options.uuid,
                    editable: this.options.editable,
                    label: 'Sample Span',
                    icon: 'fa fa-sample',
                    command: null,
		    queryState: function(event) {
			return button.hallobutton('checked', !!getEnclosing("samp"));
		    }
                });
 
                toolbar.append(button);
 
                button.on('click', function(event) {
		    lastSelection = widget.options.editable.getSelection();
		    has_ws_end = lastSelection.toString().endsWith(' ') ? ' ':''
		    if( getEnclosing("samp") ) {
			return widget.options.editable.execute('removeFormat');
		    } else {
			return widget.options.editable.execute('insertHTML', '<samp>'+lastSelection.toHtml().trim()+'</samp>'+has_ws_end);
		    }
                });
            }
        });
    })(jQuery);
}).call(this);

