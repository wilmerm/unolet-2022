/**
 * VueJs.
 * 
 * @author Unolet <www.unolet.com>
 * @copyright 2021 Unolet SRL
 */


 const app = {
    data() {
        return {
            test: "Hello World",
            document: {},
            movements: [],
            totals: {},
            movement: {
                id: null,
                item_id: null,
                item_codename: "",
                item_name: "",
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
        update_movements() {
        fetch(URLS.document_document_movement_list_json)
            .then(r => r.json())
            .then(data => {
                this.document = data.data.document;
                this.movements = data.data.movements;
                this.totals = data.data.totals;
            });
        }
    }
 }


Vue.createApp(app)

.component("item-search", {
    data() {
        return {
            search: "",
            items: [],
            count: 0,
            selected_item: {},
            TITLES: TITLES,
            URLS: URLS,
        }
    },
    props: ["items", "item"],
    template: `
        <input type="search" v-model="search" class="form-control" placeholder="..." v-on:input="onSearch">
        <table v-if="count" class="table table-sm table-hover mt-1">
            <thead>
                <th class="text-start">{{ TITLES.name }}</th>
                <th class="text-end">{{ TITLES.price }}</th>
                <th class="text-end">{{ TITLES.available }}</th>
            </thead>
            <tbody>
                <tr v-for="item in items" :id="'item-'+item.id" v-on:click="onSelect(item)">
                    <td>{{ item.codename }} | {{ item.name }}</td>
                    <td class="text-end">{{ item.max_price }}</td>
                    <td class="text-end">{{ item.available }}</td>
                </tr>
            </tbody>
        </table>
        <div class="container-fluid">
            <div class="row">
                <div class="col col-12 col-sm-6 col-md-4 col-lg-3>
                    <label for="id_movement_>{{ TITLES.code }}</label>
                </div>
            </div>
        </div>
    `,
    methods: {
        onSearch() {
            fetch(URLS.inventory_item_list_json + "?q=" + this.search)
                .then(r => r.json())
                .then(data => {
                    this.items = data.data.items;
                    this.count = data.data.count;
                });
        },
        onSelect(item) {
            this.selected_item = item;
        }
    }
})

.mount("#document-form-app");


