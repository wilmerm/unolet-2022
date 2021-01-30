/**
 * VueJs.
 * 
 * @author Unolet <https://www.unolet.com>
 * @copyright 2021 Unolet SRL
 */


 const app = {
    data() {
        return { 
            // Datos del documento.
            message: {
                title: "",
                content: "",
            },
            content_new_note: "", // Usado para agregar una nueva nota al documento.
            document: {
                currency: null,
            },
            notes: [],
            movements: [], // Movimientos del documento.
            totals: {}, // Totales en los movimientos.

            // Formulario de edición o creación de movimiento.
            movement: { 
                id: null,
                item_id: null,
                item__codename: "",
                item__name: "",
                name: "",
                quantity: 0,
                available: 0,
                price: 0,
                min_price: 0,
                discount_percent: 0,
                discount: 0,
                tax: 0,
                tax_already_included: false,
                total: 0,
            },

            select_all_movements: false, // checkbox que seleciona todos los movimientos.
            
            // Movimiento selecionado para eliminarse en espera de confirmación del usuario.
            selected_movement_for_delete: {
                id: null,
                number: null, 
                name: "",
            }, 

            // Errores del formulario de movimientos.
            errors: {
                global: [],
                document: [],
                item: [],
                name: [],
                quantity: [],
                price: [],
                discount: [],
            },
            
            // Campo de búsqueda de artículos en el formulario de movimientos.
            search: {
                text: "", // Texto ingresado en la búsqueda.
                items: [], // Resultado de la búsqueda.
                count: 0, // Cantidad de resultados.
                selected_item: {}, // Item seleccionado.
            },
            
            CSRF_TOKEN: CSRF_TOKEN,
            DOCUMENT_PK: DOCUMENT_PK,
            TITLES: TITLES,
            URLS: URLS,
            USER_ID: USER_ID,

            timeout_on_search: "",
        }
    },

    mounted() {
        if (this.DOCUMENT_PK) {
            this.update();
        }
    },

    methods: {
        intcomma(num) {
            try {
                return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            } catch (error) {
                return num;
            }
        },

        // Actualiza los datos del documento, movimientos, notas, etc.
        update() {
            fetch(URLS.api_document_document_detail)
                .then(r => r.json())
                .then(data => {
                    this.document = data.data.document;
                    this.notes = data.data.notes;
                    this.movements = data.data.movements;
                    this.totals = data.data.totals;
                });
        },
        
        // Al seleccionar un artículo en el formulario de movimiento.
        onSelect(item) {
            this.movement.item_id = item.id;
            this.movement.item__codename = item.codename;
            this.movement.name = item.name;
            this.movement.available = item.available;
            this.movement.price = item.max_price;
            this.search.selected_item = item;
            this.search = {
                text: "",
                items: [],
                count: 0, 
                selected_item: {}
            }
        },

        // Al buscar un artículo en el formulario de movimiento.
        onSearch() {
            clearTimeout(this.timeout_on_search);
            this.timeout_on_search = setTimeout(this.searchItems, 1000);
        },
        
        searchItems() {
            fetch(URLS.api_inventory_item_list + "?q=" + this.search.text)
                .then(r => r.json())
                .then(data => {
                    this.search.items = data.data.items;
                    this.search.count = data.data.count;
                });
        },
        
        // Muestra el cuadro modal con el id indicado.
        showModal(modal_id) {
            let modalEl = document.getElementById(modal_id);
            let modal = new bootstrap.Modal(modalEl);
            modal.show();
        },

        // Evento al agregar una nota.
        onAddNote() {
            if (!this.content_new_note) {
                this.message.content = this.TITLES.write_something;
                this.message.title = this.TITLES.write_something;
                this.showModal("message-modal");
                return;
            }

            let formData = new FormData();
            formData.append("content", this.content_new_note);

            fetch(URLS.api_document_document_documentnote_create, {
                method: 'POST',
                headers: {'X-CSRFToken': this.CSRF_TOKEN},
                body: formData,
                mode: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                // Si ocurren errores en el servidor.
                if (data.errors) {
                    try {
                        this.errors = JSON.parse(data.errors);
                    } catch (error) {
                        this.errors = data.errors;
                    }
                } else {
                    this.content_new_note = "";
                    this.update();
                }
            });
        },

        // Elimina la nota con el id indicado.
        // El servidor solo permite que el usuario que las creó las pueda eliminar.
        onDeleteNote(note_id) {
            let formData = new FormData();
            formData.append("id", note_id);

            fetch(URLS.api_document_document_documentnote_delete, {
                method: 'POST',
                headers: {'X-CSRFToken': this.CSRF_TOKEN},
                body: formData,
                mode: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                // Si ocurren errores en el servidor.
                if (data.errors) {
                    try {
                        this.errors = JSON.parse(data.errors);
                    } catch (error) {
                        this.errors = data.errors;
                    }
                } else {
                    this.update();
                }
            });
        },

        // Abre el formulario para agregar un nuevo movimiento.
        onAddMovement() {
            if (!this.DOCUMENT_PK) {
                this.showModal("message-modal");
                this.message.title = this.TITLES.you_must_save_the_document;
                this.message.content = this.TITLES.you_must_save_the_document_to_add_movements;
                return;
            }
            this.showModal("movement-add-modal");
        },

        // Abre el formulario para editar un movimiento.
        onEditMovement(movement) {
            this.showModal("movement-add-modal");
            this.movement = movement;
        },

        // Abre el cuadro de confirmación para eliminar un movimiento.
        onDeleteMovement(movement) {
            this.selected_movement_for_delete = movement;
            this.showModal("movement-confirm-delete-modal");
        },
        
        // Al cancelar la eliminación de un movimiento.
        onCancelDeleteMovement() {
            this.selected_movement_for_delete = {id: null, number: null, name: ""};
        },

        // Al confirmar la eliminación del movimiento, este se eliminará.
        onConfirmDeleteMovement() {
            let formData = new FormData();
            formData.append("id", this.selected_movement_for_delete.id);

            fetch(URLS.api_inventory_movement_delete, {
                method: 'POST',
                headers: {'X-CSRFToken': this.CSRF_TOKEN},
                body: formData,
                mode: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                // Si ocurren errores en el servidor.
                if (data.errors) {
                    try {
                        this.errors = JSON.parse(data.errors);
                    } catch (error) {
                        this.errors = data.errors;
                    }
                } else {
                    this.selected_movement_for_delete = {id: null, number: null, name: ""};
                    this.update();
                }
            });
        },

        // Al guardar el movimiento.
        onSaveMovement() {
            let formData = new FormData();
            formData.append("id", this.movement.id);
            formData.append("document", this.DOCUMENT_PK);
            formData.append("item", this.movement.item_id);
            formData.append("name", this.movement.name);
            formData.append("quantity", this.movement.quantity);
            formData.append("price", this.movement.price);
            formData.append("discount_percent", this.movement.discount_percent);
            formData.append("discount", this.movement.discount);
            formData.append("tax_already_included", this.movement.tax_already_included);

            console.log(this.movement.id, this.DOCUMENT_PK, this.movement.item_i)

            fetch(URLS.api_inventory_movement_form, {
                method: 'POST',
                headers: {'X-CSRFToken': this.CSRF_TOKEN},
                body: formData,
                mode: 'same-origin'})
                .then(response => response.json())
                .then(data => {
                    // Si ocurren errores en el servidor.
                    if (data.errors) {
                        try {
                            this.errors = JSON.parse(data.errors);
                        } catch (error) {
                            this.errors = data.errors;
                        }
                        console.error(data.errors);
                    } else {
                        let modalEl = document.getElementById('movement-add-modal');
                        let modal = bootstrap.Modal.getInstance(modalEl);
                        modal.hide();
                        this.update();
                        this.reset();
                    }
                });
        },

        // Click para imprimir el documento.
        onPrintDocument: function() {
            
        },

        // Reestablece las variables a los valores iniciales.
        reset() {
            this.movement = {
                id: null,
                item_id: null,
                item__codename: "",
                item__name: "",
                name: "",
                quantity: 0,
                available: 0,
                price: 0,
                min_price: 0,
                discount_percent: 0,
                discount: 0,
                tax: 0,
                tax_already_included: false,
                total: 0,
            }
            this.search = {
                text: "", // Texto ingresado en la búsqueda.
                items: [], // Resultado de la búsqueda.
                count: 0, // Cantidad de resultados.
                selected_item: {}, // Item seleccionado.
            }
        }
    }
 }


Vue.createApp(app)
// ---
.mount("#document-form-app");


