<style>
    td.up {
        background-color: #90EE90;
    }

    td.freeze {
        background-color: #C0C0C0;
    }

    td.down {
        background-color: #F08080;
    }

    td.unselected {
        opacity: 0.4;
    }
</style>
<template>
    <table class="pure-table pure-table-bordered" style="width:100%;">
        <thead>
            <tr>
                <th>HOME</th>
                <th>AWAY</th>
                <th>DRAW</th>
                <th>TOTAL</th>
                <th>OVER</th>
                <th>UNDER</th>
            </tr>
        </thead>

        <tbody>
            <tr>
                <td v-bind:class="getClass(odds_diff.homeDiff)">{{odds_diff.homeDiff}}</td>
                <td v-bind:class="getClass(odds_diff.awayDiff)">{{odds_diff.awayDiff}}</td>
                <td v-bind:class="getClass(odds_diff.drawDiff)">{{odds_diff.drawDiff}}</td>
                <td v-bind:class="getClass(odds_diff.totalPointsDiff)">{{odds_diff.totalPointsDiff}}</td>
                <td v-bind:class="getClass(odds_diff.totalOverDiff)">{{odds_diff.totalOverDiff}}</td>
                <td v-bind:class="getClass(odds_diff.totalUnderDiff)">{{odds_diff.totalUnderDiff}}</td>
            </tr>
        </tbody>
    </table>
</template>

<script>

export default {
    props: ['odds_diff'],
    methods: {
        getClass(value) {
            if (value > 0) return "up";
            if (value < 0) return "down";
            return "freeze";
        }
    }
}
</script>
