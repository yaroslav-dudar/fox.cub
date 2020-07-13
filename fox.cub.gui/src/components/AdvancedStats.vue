<template>
    <div>
        <table class="pure-table">
            <thead>
                <tr>
                    <th>Variance Team</th>
                    <th>Variance Opponents</th>
                </tr>
            </thead>
            <tr>
                <td>{{getVariance(team_dataset)}}</td>
                <td>{{getVariance(opponent_dataset)}}</td>
            </tr>
        </table>
    </div>
</template>

<script>

export default {
    props: ['team_dataset', 'opponent_dataset'],
    methods: {
        getAvg(data) {
            return data.reduce((pr, cr) => pr + cr) / data.length;
        },

        getVariance(observations) {
            var obs_avg = this.getAvg(observations);
            var data = observations.map(ob => Math.pow(ob - obs_avg, 2));
            return this.getAvg(data);
        }
    }
}
</script>
