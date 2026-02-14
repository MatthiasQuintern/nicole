# Maintainer: Matthias Quintern <matthias(dot)quintern(at)posteo(dot)de>
pkgname=nicole
pkgver=2.1.1
pkgrel=3
pkgdesc="Write lyrics from genius or azlyrics.com to a mp3-tag"
arch=('any')
url="https:/github.com/MatthiasQuintern/nicole"
license=('GPL3')
depends=('python-mutagen' 'python-beautifulsoup4')
source=(file://${PWD}/nicole/nicole.py _nicole.compdef.zsh nicole.1.man)
sha256sums=(ec362dc4f625c689d93b5caa2aef9091cfd87577c7dcf41afada18882b7a9802 2a872b395b8ac68243b5f5e53a79486a9b12b8fca890a02472c833bd427208b9 363d1cbefae32c4fadcfd521e3c890691817285e6cce3cfbe6f4e3b2b644a9e2)

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
