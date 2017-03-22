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
    return $.widget("IKS.htmlbutton", {
      options: {
        editable: null,
        toolbar: null,
        uuid: "",
        lang: 'en',
        dialogOpts: {
          autoOpen: false,
          width: 800,
          height: 'auto',
          modal: true,
          resizable: true,
          draggable: true,
          dialogClass: 'htmledit-dialog'
        },
        dialog: null,
        buttonCssClass: null
      },
      translations: {
        en: {
          title: 'Edit HTML',
          update: 'Update'
        },
        de: {
          title: 'HTML bearbeiten',
          update: 'Aktualisieren'
        }
      },
      texts: null,
      populateToolbar: function($toolbar) {
        var $buttonHolder, $buttonset, id, selector, widget;
        widget = this;
        this.texts = this.translations[this.options.lang];
        this.options.toolbar = $toolbar;
        selector = "" + this.options.uuid + "-htmledit-dialog";
        this.options.dialog = $("<div>").attr('id', selector);
        $buttonset = $("<span>").addClass(widget.widgetName);
        id = "" + this.options.uuid + "-htmledit";
        $buttonHolder = $('<span>');
        $buttonHolder.hallobutton({
          label: this.texts.title,
          icon: 'fa fa-pencil',
          editable: this.options.editable,
          command: null,
          queryState: false,
          uuid: this.options.uuid,
          cssClass: this.options.buttonCssClass
        });
        $buttonset.append($buttonHolder);
        this.button = $buttonHolder;
        this.button.click(function() {
          if (widget.options.dialog.dialog("isOpen")) {
            widget._closeDialog();
          } else {
            widget._openDialog();
          }
          return false;
        });
        this.options.editable.element.on("hallodeactivated", function() {
          return widget._closeDialog();
        });
        $toolbar.append($buttonset);
        this.options.dialog.dialog(this.options.dialogOpts);
        return this.options.dialog.dialog("option", "title", this.texts.title);
      },
      _openDialog: function() {
        var $editableEl, html, widget, xposition, yposition,
          _this = this;
        widget = this;
        $editableEl = $(this.options.editable.element);
        xposition = $editableEl.offset().left + $editableEl.outerWidth() + 10;
        yposition = this.options.toolbar.offset().top - $(document).scrollTop();
        this.options.dialog.dialog("option", "position", [xposition, yposition]);
        this.options.editable.keepActivated(true);
        this.options.dialog.dialog("open");
        this.options.dialog.on('dialogclose', function() {
          $('label', _this.button).removeClass('ui-state-active');
          _this.options.editable.element.focus();
          return _this.options.editable.keepActivated(false);
        });
        this.options.dialog.html($("<textarea>").addClass('html_source'));
        html = this.options.editable.element.html();
        this.options.dialog.children('.html_source').val(html);
        this.options.dialog.prepend($("<button>" + this.texts.update + "</button>"));
        return this.options.dialog.on('click', 'button', function() {
          html = widget.options.dialog.children('.html_source').val();
          widget.options.editable.element.html(html);
          widget.options.editable.element.trigger('change');
          return false;
        });
      },
      _closeDialog: function() {
        return this.options.dialog.dialog("close");
      }
    });
  })(jQuery);

}).call(this);
