# ptmnavigator

## How to (locally) embed this into another Vue project:

- In this project: configure `vue.config.js` for library export (it currently already is, so you can copy-paste this for
  future projects)
- In the parent project, in the component where you want to load it, use it like this
  (assuming you have a custom API implemented already)

```
<template>
    <ptm-navigator
      :backend-api="ptmnavigatorBackend"
      :ptm-navigator-router="router"
    />
</template>

<script>
import { PTMNavigator } from 'ptmnavigator'
import myCustomAPI from '../../plugins/myCustomAPI'

export default {
  name: 'PTMNavigatorWrapper',
  components: {
    'ptm-navigator': PTMNavigator
  },
  data () {
    return {
      ptmnavigatorBackend: ptmNavigatorPrdbApi,
      router: this.$router
    }
  }
}
</script>
```

- Then, build PTMNavigator (in `frontend` package): `npm run build` (I _think_ you don't have to call `npm link` from
  here, but try it out in case it doesn't work).
- In the main component establish the link with: `npm link ptmnavigator`   

From now on, everytime you make changes and want them to show in your parent component:
- `npm run build` (in PTMNavigator/frontend)
- Shutdown server of the main component
- `rm -rf node_modules/.cache/`
- Restart server with `npm run serve`

## Project setup

```
npm install
```

### Compiles and hot-reloads for development

```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
