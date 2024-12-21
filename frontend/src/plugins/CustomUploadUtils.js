import axios from 'axios'

const utils = {

  async renewSession (host, uuid) {
    //TODO: Refactor into backend
    await axios.get(
      host +
            '/proteomicsdb/logic/secure/refreshUUID.xsjs',
      { params: { uuid } }
    )
    this.expiry_days = 14
  }
}

export default utils
