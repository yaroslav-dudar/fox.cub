<template>
    <table class="pure-table pure-table-bordered center">
        <thead>
            <tr>
                <th>{{key_name}}</th>
                <th>{{value_name}}</th>
            </tr>
        </thead>
        <tr  v-for="k in Object.keys(table_data)" :key="k">
            <td><strong>{{k}}</strong></td>
            <td>{{table_data[k]}}</td>
        </tr>

    </table>
</template>

<script>


export default {
    props: ['table_data', 'key_name', 'value_name']

}
</script>
