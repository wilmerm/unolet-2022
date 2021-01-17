
  
const app = {
    data() {
        return {
            movements: ['hola', 'mundo'],
        }
    },
}

Vue.createApp(app).component("items", {
    props: ["obj"],
    template: `
        <tr>
            <td>
                <a href="#" class="py-0 px-1">{% svg 'pencil-fill' size='1rem' %}</a>
                <a href="#" class="py-0 px-1">{% svg 'x-circle-fill' size='1rem' %}</a>
            </td>
            <td><input type="checkbox"></td>
            <td>{% vue 'obj.number' %}</td>
            <td>{% vue 'obj.item__codename' %}</td>
            <td>{% vue 'obj.name' %}</td>
            <td class="text-end">{% vue 'intcomma(obj.quantity)' %}</td>
            <td class="text-end">{% vue 'intcomma(obj.price)' %}</td>
            <td class="text-end">{% vue 'intcomma(obj.discount)' %}</td>
            <td class="text-end">{% vue 'intcomma(obj.tax)' %}</td>
            <td class="text-end">{% vue 'intcomma(obj.total)' %}</td>
        </tr>`
}).mount("#test-app")