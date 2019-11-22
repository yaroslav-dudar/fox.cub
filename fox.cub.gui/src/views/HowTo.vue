<style lang="scss">
div.content {
    font-family: 'Courier New', Courier, monospace;
    font-size: 24px;
}
div.content ul {
    text-align: left;
}

div.content section {
    background-color: #42b983;
    background-clip: content-box;
    padding: 50px;
}
</style>

<template>
    <div class="content">
        <section>
            <h2>Steps to procced before making a bet:</h2>
            <ul>
                <li>Calculate probabilities with statistical model</li>
                <li>Review player injuries and suspensions</li>
                <li>Evaluate risks</li>
                <li>Define teams motivation and fatigue</li>
                <li>Easy or Hard matchup. Compare team styles</li>
                <li>Betting market behavior for each team</li>
                <li>Review trends for each team</li>
                <li>Predict how managers will approach the game</li>
                <li>Review weather forecast</li>
                <li>Teams market value. Teams level of talent</li>
            </ul>
        </section>

        <section>
            <h2>Notes about team without the ball:</h2>
            <ul>
                <li>What's intensity without the ball</li>
                <li>How much space and time team give to the oposition</li>
                <li>Compactness, shape and discipline without the ball</li>
                <li>One-vs-One defending</li>
                <li>Communication</li>
                <li>Controlling games without the ball</li>
            </ul>
        </section>

        <section>
            <h2>Notes about team with the ball:</h2>
            <ul>
                <li>How quickly team move the ball</li>
                <li>Movement of pleyers without the ball</li>
                <li>Team structure, maximising passing lanes and support player with the ball</li>
                <li>How often team get in opposition dangerous areas</li>
                <li>Ability to break the lines of pressure</li>
                <li>Quality of chances created </li>
                <li>Controlling games with the ball</li>
            </ul>
        </section>

        <section>
            <h2>Notes about mentality:</h2>
            <ul>
                <li>Players body language and attitude</li>
                <li>Ability to change run of play</li>
                <li>Reaction to failures and bad luck</li>
                <li>Leadership</li>
                <li>Sacrifice for the result of the game</li>
            </ul>
        </section>
    </div>

</template>

<script>

export default {
    name: 'HowTo',
    data: function() {
        return {}
    }
}
</script>
