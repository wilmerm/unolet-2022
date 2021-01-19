/**
 * VueJs.
 * 
 * @author Unolet <www.unolet.com>
 * @copyright 2021 Unolet SRL
 */


 const app = {
    data() {
        return {
            document: {}, // Datos del documento.
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
        }
    },

    mounted() {
        this.update_movements();
    },

    methods: {
        intcomma(num) {
            try {
                return num.toString().replace(/B(?=(d{3})+(?!d))/g, ",");
            } catch (error) {
                return num;
            }
        },

        // Actualiza el listado de movimientos.
        update_movements() {
            fetch(URLS.document_document_movement_list_json)
                .then(r => r.json())
                .then(data => {
                    this.document = data.data.document;
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
        },

        // Al buscar un artículo en el formulario de movimiento.
        onSearch() {
            fetch(URLS.inventory_item_list_json + "?q=" + this.search.text)
                .then(r => r.json())
                .then(data => {
                    this.search.items = data.data.items;
                    this.search.count = data.data.count;
                });
        },

        // Abre el formulario para editar un movimiento.
        onEditMovement(movement) {
            var modalEl = document.getElementById("movement-add-modal");
            var modal = new bootstrap.Modal(modalEl);
            modal.show();
            this.movement = movement;
        },

        // Al guardar el movimiento.
        onSaveMovement() {
            var formData = new FormData();
            formData.append("id", this.movement.id);
            formData.append("document", this.DOCUMENT_PK);
            formData.append("item", this.movement.item_id);
            formData.append("name", this.movement.name);
            formData.append("quantity", this.movement.quantity);
            formData.append("price", this.movement.price);
            formData.append("discount_percent", this.movement.discount_percent);
            formData.append("discount", this.movement.discount);
            formData.append("tax_already_included", this.movement.tax_already_included);

            fetch(URLS.inventory_movement_form_json, {
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
                    } else {
                        let modalEl = document.getElementById('movement-add-modal');
                        let modal = bootstrap.Modal.getInstance(modalEl);
                        modal.hide();
                        this.update_movements();
                        this.reset();
                    }
                });
        },

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

// .component("item-search", {
//     data() {
//         return {
//             search: "",
//             items: [],
//             count: 0,
//             selected_item: {},
//             TITLES: TITLES,
//             URLS: URLS,
//         }
//     },
//     props: ["items", "item"],
//     template: `
//         <input type="search" v-model="search" class="form-control" placeholder="..." v-on:input="onSearch">
//         <table v-if="count" class="table table-sm table-hover mt-1">
//             <thead>
//                 <th class="text-start">{{ TITLES.name }}</th>
//                 <th class="text-end">{{ TITLES.price }}</th>
//                 <th class="text-end">{{ TITLES.available }}</th>
//             </thead>
//             <tbody>
//                 <tr v-for="item in items" :id="'item-'+item.id" v-on:click="onSelect(item)">
//                     <td>{{ item.codename }} | {{ item.name }}</td>
//                     <td class="text-end">{{ item.max_price }}</td>
//                     <td class="text-end">{{ item.available }}</td>
//                 </tr>
//             </tbody>
//         </table>
//         <div class="container-fluid">
//             <div class="row">
//                 <div class="col col-12 col-sm-6 col-md-4 col-lg-3>
//                     <label for="id_movement_>{{ TITLES.code }}</label>
//                 </div>
//             </div>
//         </div>
//     `,
//     methods: {
//         onSearch_____() {
//             fetch(URLS.inventory_item_list_json + "?q=" + this.search)
//                 .then(r => r.json())
//                 .then(data => {
//                     this.items = data.data.items;
//                     this.count = data.data.count;
//                 });
//         },
//         onSelect_____(item) {
//             this.selected_item = item;
//             this.movement.item_id = item;
//         },
//     }
// })

.mount("#document-form-app");


