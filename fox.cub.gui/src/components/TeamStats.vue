<template>
    <div >
        <table class="pure-table" style="width: 80%">
            <thead>
                <tr>
                    <th>Actual goals scored</th>
                    <th>Actual goals conceded</th>
                </tr>
            </thead>
            <tr>
                <td v-if="stats.actual">{{stats.actual.scored.toFixed(3)}}</td>
                <td v-else> No data </td>
                <td v-if="stats.actual">{{stats.actual.conceded.toFixed(3)}}</td>
                <td v-else> No data </td>
            </tr>
        </table>
        <table class="pure-table" style="width: 80%">
            <thead>
                <tr>
                    <th>Expected goals scored</th>
                    <th>Expected goals conceded</th>
                </tr>
            </thead>
            <tr>
                <td v-if="stats.xg">{{stats.xg.scored.toFixed(3)}}</td>
                <td v-else> No data </td>
                <td v-if="stats.xg">{{stats.xg.conceded.toFixed(3)}}</td>
                <td v-else> No data </td>
            </tr>
        </table>
    </div>
</template>

<script>
export default {
    props: ['stats']
}
</script>
