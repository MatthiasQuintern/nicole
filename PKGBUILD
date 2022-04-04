# Maintainer: Matthias Quintern <matthiasqui@protonmail.com>
pkgname=nicole
pkgver=2.0
pkgrel=1
pkgdesc="Write lyrics from genius or azlyrics.com to a mp3-tag"
arch=('any')
url="https:/github.com/MatthiasQuintern/nicole"
license=('GPL3')
depends=('python-mutagen' 'python-beautifulsoup4')
source=(file://${PWD}/nicole/nicole.py _nicole.compdef.zsh nicole.1.man)
md5sums=(93752797fc2bca526fbfd32611518065 f3b46bdcaba5e7fc23bbacc6b2e153c0 19b346a1656bb3db899635d36352dc53)

package() {
	mkdir -p "${pkgdir}/usr/bin"
	cp "${srcdir}/nicole.py" "${pkgdir}/usr/bin/nicole"
	chmod +x "${pkgdir}/usr/bin/nicole"

	mkdir -p "${pkgdir}/usr/share/man/man1/"
	cp "${srcdir}/nicole.1.man" "${pkgdir}/usr/share/man/man1/nicole.1"

	# if zsh is installed
	if [[ -f /bin/zsh ]]; then
		mkdir -p "${pkgdir}/usr/share/zsh/site-functions"
		cp "${srcdir}/_nicole.compdef.zsh" "${pkgdir}/usr/share/zsh/site-functions/_nicole"
		chmod +x "${pkgdir}/usr/share/zsh/site-functions/_nicole"
	fi
}
