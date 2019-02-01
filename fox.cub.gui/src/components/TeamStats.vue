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
                <td>{{stats.actual.scored.toFixed(3)}}</td>
                <td>{{stats.actual.conceded.toFixed(3)}}</td>
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
                <td>{{stats.xg.scored.toFixed(3)}}</td>
                <td>{{stats.xg.conceded.toFixed(3)}}</td>
            </tr>
        </table>
    </div>
</template>

<script>
export default {
    props: ['stats']
}
</script>
