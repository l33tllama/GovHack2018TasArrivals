const express = require('express')
const app = express()
app.use(require('easy-livereload')());

//app.get('/', (req, res) => res.send('Hello World!'))
app.use(express.static('.'))

app.listen(3000, () => console.log('Example app listening on port 3000!'))