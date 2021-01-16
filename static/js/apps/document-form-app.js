/**
 * VueJs.
 * 
 * @author Unolet <www.unolet.com>
 * @copyright 2021 Unolet SRL
 */


 const DocumentFormApp = {
     data() {
         return {
            test: "Hello World",
            movements: [],
            totals: {},
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
                console.log(num, error);
                return num;
            }
         },

         update_movements() {
            fetch(URLS.document_document_movement_list_json)
                .then(r => r.json())
                .then(data => {
                    this.movements = data.data.movements;
                    this.totals = data.data.totals;
                });
                
         }
     }
 }


 Vue.createApp(DocumentFormApp).mount("#document-form-app");