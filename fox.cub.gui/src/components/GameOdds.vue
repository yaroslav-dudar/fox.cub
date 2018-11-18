<template>
    <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>Home Win</th>
                <th>Draw</th>
                <th>Away Win</th>
                <th>Total</th>
                <th>Total Under</th>
                <th>Total Over</th>
                <th>Scraping Date</th>
            </tr>
        </thead>
        <tr v-for="(o, index) in odds_history" :key="index">
            <td>{{o.home_win}}</td>
            <td>{{o.draw}}</td>
            <td>{{o.away_win}}</td>
            <td>{{o.total}}</td>
            <td>{{o.total_under}}</td>
            <td>{{o.total_over}}</td>
            <td>{{o.scraping_date.$date}}</td>
        </tr>
    </table>
</template>

<script>
export default {
    props: ['odds_history']
}
</script>
